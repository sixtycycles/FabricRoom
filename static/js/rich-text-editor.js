/**
 * Rich Text Editor
 * Version: 1.0.0
 * Handles formatting, image uploads, and content management
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Rich text editor initializing...');

  const editor = document.getElementById('post-editor');
  const bodyInput = document.getElementById('id_body');
  const postForm = document.getElementById('blog-post-form');

  // Get all the toolbar elements
  const headingDropdown = document.getElementById('heading-dropdown');
  const headingMenu = document.getElementById('heading-menu');
  const linkBtn = document.getElementById('link-btn');
  const linkDialog = document.getElementById('link-dialog');
  const linkUrlInput = document.getElementById('link-url');
  const linkApplyBtn = document.getElementById('link-apply');
  const linkCancelBtn = document.getElementById('link-cancel');
  const imageBtn = document.getElementById('image-btn');
  const imageUploadForm = document.getElementById('image-upload-form');
  const imageFileInput = document.getElementById('image-file-input');
  const imageCancelBtn = document.getElementById('image-cancel');
  const imageUploadBtn = document.getElementById('image-upload-btn');
  const imageAltModal = document.getElementById('image-alt-modal');
  const imageAltInput = document.getElementById('image-alt-input');
  const imageAltCancelBtn = document.getElementById('image-alt-cancel');
  const imageAltConfirmBtn = document.getElementById('image-alt-confirm');

  const pendingImageUploads = [];
  let pendingImageFile = null;
  let pendingButtonAltText = null;

  console.log('Editor:', editor);
  console.log('Body input:', bodyInput);
  console.log('Form:', postForm);

  if (!editor || !bodyInput || !postForm) {
    console.error('Missing required elements');
    return;
  }

  console.log('All elements found, setting up form handler');

  // Initialize editor with existing content
  if (bodyInput.value) {
    console.log('Initializing editor with existing content');
    editor.innerHTML = bodyInput.value;
  }

  // Setup drag and drop for file uploads
  setupDragAndDrop();

  // Setup image editing features
  setupImageEditing();

  // Simple form submit handler
  postForm.addEventListener('submit', function(e) {
    console.log('FORM SUBMIT EVENT FIRED!!!');
    bodyInput.value = editor.innerHTML;
    console.log('Body value set to:', bodyInput.value.substring(0, 50));
    console.log('Title value:', postForm.querySelector('input[name="title"]').value);
    // Let form submit normally
  });

  // Also add click handler to submit button directly
  const submitBtn = postForm.querySelector('input[type="submit"]');
  if (submitBtn) {
    console.log('Submit button found, adding click handler');
    submitBtn.addEventListener('click', function(e) {
      console.log('!!! SUBMIT BUTTON CLICKED !!!');
      bodyInput.value = editor.innerHTML;
    });
  } else {
    console.error('Submit button NOT found');
  }

  // Make editor editable
  if (editor) {
    editor.addEventListener('blur', saveContent);
    editor.addEventListener('paste', handlePaste);
  }

  // Heading dropdown toggle
  if (headingDropdown) {
    headingDropdown.addEventListener('click', function(e) {
      e.preventDefault();
      headingMenu.style.display = headingMenu.style.display === 'none' ? 'flex' : 'none';
    });
  }

  // Editor commands (bold, italic, etc)
  const editorCommands = document.querySelectorAll('.editor-command');
  editorCommands.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const command = this.dataset.command;
      const value = this.dataset.value || null;

      // Focus editor before executing command
      editor.focus();

      if (value) {
        document.execCommand(command, false, value);
      } else {
        document.execCommand(command, false, null);
      }

      // Hide heading menu after selection
      if (headingMenu) {
        headingMenu.style.display = 'none';
      }

      editor.focus();
      saveContent();
    });
  });

  // Link insertion
  if (linkBtn) {
    linkBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const selection = window.getSelection();

      if (!selection.toString()) {
        alert('Please select text to create a link');
        return;
      }

      linkDialog.style.display = 'block';
      linkUrlInput.focus();
      linkUrlInput.value = '';
    });
  }

  // Apply link
  if (linkApplyBtn) {
    linkApplyBtn.addEventListener('click', function() {
      const url = linkUrlInput.value.trim();

      if (!url) {
        alert('Please enter a URL');
        return;
      }

      // Ensure URL has protocol
      let finalUrl = url;
      if (!url.match(/^https?:\/\//)) {
        finalUrl = 'https://' + url;
      }

      editor.focus();
      document.execCommand('createLink', false, finalUrl);
      linkDialog.style.display = 'none';
      saveContent();
    });
  }

  // Cancel link dialog
  if (linkCancelBtn) {
    linkCancelBtn.addEventListener('click', function() {
      linkDialog.style.display = 'none';
    });
  }

  // Allow pressing Enter key in link input
  if (linkUrlInput) {
    linkUrlInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        linkApplyBtn.click();
      }
    });
  }

  // Image upload
  if (imageBtn) {
    imageBtn.addEventListener('click', function(e) {
      e.preventDefault();
      startImageButtonUploadFlow();
    });
  }

  // Auto-upload on file selection
  if (imageFileInput) {
    imageFileInput.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const postAltText = getPostAltText();
        Array.from(this.files).forEach(file => handleImageUpload(file, postAltText));
        imageFileInput.value = '';
      }
    });
  }

  // Cancel image upload
  if (imageCancelBtn) {
    imageCancelBtn.addEventListener('click', function() {
      imageUploadForm.style.display = 'none';
      imageFileInput.value = ''; // Clear the file input
    });
  }

  // Handle image upload button click
  if (imageUploadBtn) {
    imageUploadBtn.addEventListener('click', function(e) {
      e.preventDefault();
      if (!imageFileInput.files || !imageFileInput.files[0]) {
        alert('Please select an image file');
        return;
      }
      const postAltText = getPostAltText();
      Array.from(imageFileInput.files).forEach(file => handleImageUpload(file, postAltText));
      imageFileInput.value = '';
    });
  }

  if (imageAltCancelBtn) {
    imageAltCancelBtn.addEventListener('click', function() {
      if (imageAltModal && imageAltModal.dataset.uploadFlow === 'button') {
        delete imageAltModal.dataset.uploadFlow;
        closeAltTextModal();
        return;
      }

      closeAltTextModal();
      processNextPendingImage();
    });
  }

  if (imageAltConfirmBtn) {
    imageAltConfirmBtn.addEventListener('click', function() {
      const altText = (imageAltInput.value || '').trim();
      if (!altText) {
        alert('Alt text is required to upload an image.');
        imageAltInput.focus();
        return;
      }

      if (imageAltModal && imageAltModal.dataset.uploadFlow === 'button') {
        pendingButtonAltText = altText;
        delete imageAltModal.dataset.uploadFlow;
        closeAltTextModal();
        triggerImageFilePicker();
        return;
      }

      const fileToUpload = pendingImageFile;
      closeAltTextModal();

      if (fileToUpload) {
        handleImageUpload(fileToUpload, altText);
      }

      processNextPendingImage();
    });
  }

  if (imageAltInput) {
    imageAltInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (imageAltConfirmBtn) {
          imageAltConfirmBtn.click();
        }
      }
    });
  }

  // Save content to hidden input
  function saveContent() {
    if (editor && bodyInput) {
      bodyInput.value = editor.innerHTML;
    }
  }

  // Handle paste to strip formatting
  function handlePaste(e) {
    e.preventDefault();

    // Get plain text from clipboard
    let text;
    if (e.clipboardData || e.originalEvent.clipboardData) {
      text = (e.originalEvent || e).clipboardData.getData('text/plain');
    } else if (window.clipboardData) {
      text = window.clipboardData.getData('Text');
    }

    if (!text) return;

    // Insert plain text without formatting
    if (document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, text);
    } else {
      // Fallback for older browsers
      document.execCommand('paste', false, text);
    }

    saveContent();
  }

  // Get post ID from URL or form
  function getPostId() {
    // Check URL for post ID (e.g., /blog/post/123/update)
    const urlMatch = window.location.pathname.match(/\/post\/(\d+)\//);
    if (urlMatch) {
      return urlMatch[1];
    }

    // For new posts, return null
    return null;
  }

  function getPostAltText() {
    const postAltTextInput = document.getElementById('id_inline_image_alt_text');
    if (!postAltTextInput) {
      return 'Blog image';
    }

    const value = (postAltTextInput.value || '').trim();
    return value || 'Blog image';
  }

  // Handle image file upload
  function handleImageUpload(file, altText) {
    const postId = getPostId();
    let uploadUrl;

    // Determine the correct upload URL
    if (postId) {
      uploadUrl = `/blog/post/${postId}/upload-image/`;
    } else {
      // For new posts, use the 'new' endpoint
      uploadUrl = `/blog/post/new/upload-image/`;
    }

    if (!file) {
      alert('Please select an image file');
      return;
    }

    const resolvedAltText = (altText || '').trim() || getPostAltText();
    const postAltText = getPostAltText();

    const formData = new FormData();
    formData.append('image', file);
    formData.append('alt_text', resolvedAltText);
    formData.append('post_alt_text', postAltText);

    // Make request to upload endpoint
    fetch(uploadUrl, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Insert image into editor
          editor.focus();
          const imgHtml = `<img src="${data.image_url}" alt="${escapeHtmlAttribute(data.alt_text || resolvedAltText)}" class="editor-image img-fluid" draggable="true" data-image-id="${data.image_id}">`;
          document.execCommand('insertHTML', false, imgHtml);
          saveContent();

          // Close upload form and clear input
          imageUploadForm.style.display = 'none';

          // Setup image editing on newly added image
          setupImageEditing();
        } else {
          alert('Error uploading image: ' + (data.error || 'Unknown error'));
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error uploading image');
      });
  }

  // Setup drag and drop for file uploads and image repositioning
  function setupDragAndDrop() {
    let dragCounter = 0;

    // Highlight editor on drag over
    editor.addEventListener('dragenter', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dragCounter++;

      // Highlight for both files and image repositioning
      if (e.dataTransfer.types && (e.dataTransfer.types.includes('Files') || draggedImage)) {
        editor.style.backgroundColor = '#f0f0f0';
        editor.style.borderColor = '#007bff';
        editor.style.borderStyle = 'dashed';
      }
    });

    // Remove highlight when not dragging
    editor.addEventListener('dragleave', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dragCounter--;

      if (dragCounter === 0) {
        editor.style.backgroundColor = '';
        editor.style.borderColor = '';
        editor.style.borderStyle = '';
      }
    });

    // Allow drop for files and image repositioning
    editor.addEventListener('dragover', function(e) {
      if (e.dataTransfer.types && (e.dataTransfer.types.includes('Files') || draggedImage)) {
        e.preventDefault();
        e.stopPropagation();
        e.dataTransfer.dropEffect = draggedImage ? 'move' : 'copy';
      }
    });

    // Handle drop for files and image repositioning
    editor.addEventListener('drop', function(e) {
      dragCounter = 0;

      // Reset styling
      editor.style.backgroundColor = '';
      editor.style.borderColor = '';
      editor.style.borderStyle = '';

      // Check if files were dropped
      if (e.dataTransfer.types && e.dataTransfer.types.includes('Files')) {
        e.preventDefault();
        e.stopPropagation();

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
          // Upload dropped image files
          Array.from(files).forEach(file => {
            if (file.type.startsWith('image/')) {
              uploadImageFile(file);
            }
          });
        }
      } else if (draggedImage) {
        // Handle image repositioning
        e.preventDefault();
        e.stopPropagation();

        // Get the drop position
        const range = document.caretRangeFromPoint(e.clientX, e.clientY);

        if (range && editor.contains(range.commonAncestorContainer)) {
          // Remove the image from its current location
          const clonedImage = draggedImage.cloneNode(true);
          draggedImage.remove();

          // Insert at the new location
          range.insertNode(clonedImage);

          // Re-setup image editing for moved image
          setupImageEditing();
          saveContent();
        }
      }
    });
  }

  // Upload a file
  function uploadImageFile(file) {
    handleImageUpload(file, getPostAltText());
  }

  function startImageButtonUploadFlow() {
    pendingButtonAltText = null;
    triggerImageFilePicker();
  }

  function triggerImageFilePicker() {
    if (!imageFileInput) {
      pendingButtonAltText = null;
      alert('Image picker is unavailable. Refresh and try again.');
      return;
    }

    // If the native picker is canceled, clear any pending alt text state.
    const clearPendingAltTextOnFocus = function() {
      window.removeEventListener('focus', clearPendingAltTextOnFocus);
      window.setTimeout(function() {
        if (pendingButtonAltText && (!imageFileInput.files || imageFileInput.files.length === 0)) {
          pendingButtonAltText = null;
        }
      }, 300);
    };

    window.addEventListener('focus', clearPendingAltTextOnFocus);
    imageFileInput.click();
  }

  function enqueueImageUpload(file) {
    pendingImageUploads.push(file);
    if (!pendingImageFile) {
      processNextPendingImage();
    }
  }

  function processNextPendingImage() {
    if (pendingImageFile || pendingImageUploads.length === 0) {
      return;
    }

    pendingImageFile = pendingImageUploads.shift();
    const modalOpened = openAltTextModal(pendingImageFile);
    if (!modalOpened) {
      const fileToUpload = pendingImageFile;
      const altText = promptForAltTextFallback(fileToUpload);
      pendingImageFile = null;

      if (fileToUpload && altText) {
        handleImageUpload(fileToUpload, altText);
      }

      processNextPendingImage();
    }
  }

  function openAltTextModal(file, suggestedAltText) {
    if (!imageAltModal || !imageAltInput) {
      console.error('Missing alt text modal elements. Falling back to browser prompt.');
      return false;
    }

    const fileName = (file && file.name) ? file.name.replace(/\.[^.]+$/, '') : '';
    if (suggestedAltText !== undefined) {
      imageAltInput.value = suggestedAltText;
    } else {
      imageAltInput.value = fileName ? `Image of ${fileName}` : '';
    }
    imageAltModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    imageAltInput.focus();
    imageAltInput.select();
    return true;
  }

  function closeAltTextModal() {
    if (imageAltModal) {
      imageAltModal.style.display = 'none';
    }
    if (imageAltInput) {
      imageAltInput.value = '';
    }
    document.body.style.overflow = '';
    pendingImageFile = null;
  }

  function promptForAltTextFallback(file) {
    const fileName = (file && file.name) ? file.name.replace(/\.[^.]+$/, '') : 'uploaded image';
    const suggestedAltText = `Image of ${fileName}`;

    while (true) {
      const enteredValue = window.prompt(
        'Describe this image for screen readers (required):',
        suggestedAltText
      );

      if (enteredValue === null) {
        return null;
      }

      const altText = enteredValue.trim();
      if (altText) {
        return altText;
      }

      alert('Alt text is required to upload an image.');
    }
  }

  function escapeHtmlAttribute(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // Setup image editing (click to select, delete, drag to move)
  function setupImageEditing() {
    const images = editor.querySelectorAll('img');

    images.forEach(img => {
      // Remove previous listeners by cloning and replacing
      const newImg = img.cloneNode(true);
      img.parentNode.replaceChild(newImg, img);

      // Add click handler
      newImg.addEventListener('click', function(e) {
        e.stopPropagation();
        selectImage(this);
      });

      // Add drag handlers for repositioning
      newImg.addEventListener('dragstart', handleImageDragStart);
      newImg.addEventListener('dragend', handleImageDragEnd);
    });
  }

  // Track which image is being dragged
  let draggedImage = null;

  function handleImageDragStart(e) {
    draggedImage = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
    this.style.opacity = '0.5';
  }

  function handleImageDragEnd(e) {
    if (draggedImage) {
      draggedImage.style.opacity = '1';
      draggedImage = null;
    }
    // Remove drop indicator if it exists
    const dropIndicator = document.getElementById('image-drop-indicator');
    if (dropIndicator) {
      dropIndicator.remove();
    }
  }

  // Select an image and show editing options
  function selectImage(imgElement) {
    // Remove previous selection
    document.querySelectorAll('.editor-image.selected').forEach(el => {
      el.classList.remove('selected');
      removeImageToolbar();
    });

    // Add selection class
    imgElement.classList.add('selected');
    imgElement.style.border = '2px solid #007bff';
    imgElement.style.padding = '4px';

    // Create and show toolbar
    showImageToolbar(imgElement);
  }

  // Show toolbar for image editing
  function showImageToolbar(imgElement) {
    removeImageToolbar(); // Remove any existing toolbar

    const toolbar = document.createElement('div');
    toolbar.id = 'image-edit-toolbar';
    toolbar.style.cssText = `
      position: absolute;
      background: #f0f0f0;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 8px;
      display: flex;
      gap: 8px;
      z-index: 1000;
      margin-top: 4px;
    `;

    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '🗑️ Delete';
    deleteBtn.style.cssText = 'padding: 4px 8px; font-size: 12px; cursor: pointer; border: 1px solid #ccc; border-radius: 3px; background: #fff;';
    deleteBtn.addEventListener('click', function(e) {
      e.preventDefault();

      const imageId = imgElement.dataset.imageId;
      if (imageId) {
        // Tell the server to delete the record and file immediately.
        fetch(`/blog/post/image/${imageId}/delete/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
        }).catch(err => console.error('Error deleting image from server:', err));
      }

      imgElement.remove();
      removeImageToolbar();
      saveContent();
      editor.focus();
    });

    toolbar.appendChild(deleteBtn);

    // Position toolbar near the image
    imgElement.parentNode.insertBefore(toolbar, imgElement.nextSibling);
  }

  // Remove image toolbar
  function removeImageToolbar() {
    const toolbar = document.getElementById('image-edit-toolbar');
    if (toolbar) {
      toolbar.remove();
    }
  }

  // Clear toolbar when clicking elsewhere
  editor.addEventListener('click', function(e) {
    if (e.target.tagName !== 'IMG') {
      removeImageToolbar();
      document.querySelectorAll('.editor-image.selected').forEach(el => {
        el.classList.remove('selected');
        el.style.border = 'none';
        el.style.padding = '0';
      });
    }
  });

  // Helper to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
