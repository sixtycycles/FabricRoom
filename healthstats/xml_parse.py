import xml.etree.ElementTree as et
tree = et.parse('/Users/rod/PycharmProjects/FabricRoom/media/apple_health_xml/export.xml')
root = tree.getroot()
for element in root:
    print(element.tag)