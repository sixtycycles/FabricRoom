## Fabric Room ###
### This is the django code to render [60hz.dev](https://60hz.dev) ###

This project is a personal website for myself. I am building tools as i need them and adding on to this app. 

to apply scss changes to css:
``` sass /Users/rod/PycharmProjects/FabricRoom/static/bootstrap-5.3.8/scss/fabricroom.scss /Users/rod/PycharmProjects/FabricRoom/static/bootstrap-5.3.8/css/fabricroom.css```


to update css on prod: 
``` scp -rp static/bootstrap-5.3.8/css/fabricroom.css rod@60hz.dev:/srv/code/static/bootstrap-5.3.8/css/fabricroom.css
fabricroom.css ```

## Superuser dashboard command triggers (systemd + sudoers)

The home dashboard now includes a **superuser-only** button to run:

- `cleanup_orphan_images`

The button triggers a POST to Django, and Django runs:

`sudo -n /bin/systemctl start fabricroom-cleanup-orphan-images.service`

You can override defaults with environment variables:

- `CLEANUP_ORPHAN_IMAGES_SYSTEMD_SERVICE`
- `MANAGEMENT_COMMAND_SUDO_PATH`
- `MANAGEMENT_COMMAND_SYSTEMCTL_PATH`

### Example systemd service + timer

`/etc/systemd/system/fabricroom-cleanup-orphan-images.service`
```ini
[Unit]
Description=FabricRoom cleanup orphan inline images

[Service]
Type=oneshot
WorkingDirectory=/srv/code/FabricRoom
User=www-data
Group=www-data
ExecStart=/srv/code/FabricRoom/venv/bin/python /srv/code/FabricRoom/manage.py cleanup_orphan_images
```

`/etc/systemd/system/fabricroom-cleanup-orphan-images.timer`
```ini
[Unit]
Description=Run FabricRoom orphan image cleanup on schedule

[Timer]
OnCalendar=hourly
Persistent=true
Unit=fabricroom-cleanup-orphan-images.service

[Install]
WantedBy=timers.target
```

Enable timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now fabricroom-cleanup-orphan-images.timer
```

### sudoers rule for web-triggered runs

Create `/etc/sudoers.d/fabricroom-www-data-systemd` with:
```sudoers
Defaults:www-data !requiretty
www-data ALL=(root) NOPASSWD: /bin/systemctl start fabricroom-cleanup-orphan-images.service
```

Validate and apply:
```bash
sudo visudo -cf /etc/sudoers.d/fabricroom-www-data-systemd
```
