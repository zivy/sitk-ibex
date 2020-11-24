#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
The image metadata dictionary contains the following keys-values:
    'unit' - string denoting the physical units of the image origin,
             and spacing.
    'times' - string denoting the time associated with the image in
                        ('%Y-%m-%d %H:%M:%S.%f' -
                        Year-month-day hour:minute:second.microsecond) format.
    'imaris_channels_information' - XML string denoting channel information.
    XML structure:

<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="imaris_channels_information">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="channel">
          <xs:complexType>
              <xs:element type="xs:string" name="name"/>
              <xs:element type="xs:string" name="description"/>
              <xs:element type="xs:string" name="color"/>
              <xs:element type="xs:string" name="range"/>
              <xs:element type="xs:string" name="gamma" minOccurs="0" maxOccurs="1"/>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
"""

import xml.etree.ElementTree as et


def channels_information_xmlstr2list(channels_information_xml_str):
    """
    Convert the xml string containing channel information into a list of dictionaries with channel information.

    :param channels_information_xml_str: xml string representation the channels information.
    :return: list of dictionaries representing the information from the input xml string
    """
    channels_information = []
    channels_xml_information = list(et.fromstring(channels_information_xml_str))
    for channel_xml_info in channels_xml_information:
        channel_info = {}
        channel_info['name'] = channel_xml_info.find('name').text
        channel_info['description'] = channel_xml_info.find('description').text
        if channel_xml_info.find('color') is not None:
            channel_info['color'] = [float(c)/255 for c in channel_xml_info.find('color').text.replace(',', ' ').split()]  # noqa: E501
        elif channel_xml_info.find('color_table') is not None:
            channel_info['color_table'] = [float(c)/255 for c in channel_xml_info.find('color_table').text.replace(',', ' ').split()]  # noqa: E501
        channel_info['range'] = [float(c) for c in channel_xml_info.find('range').text.replace(',', ' ').split()]
        if channel_xml_info.find('gamma'):  # Gamma is optional
            channel_info['gamma'] = float(channel_xml_info.find('gamma').text)
        channel_info['alpha'] = float(channel_xml_info.find('alpha').text)
        channels_information.append(channel_info)
    return channels_information


def channels_information_list2xmlstr(channels_information_list):
    """
    Convert the channels information list of dictionaries to an xml string
    representation which can be embedded as metadata in the image.

    :param channels_information_list: list of dictionaries.
    :return: an xml string representing the information from the input list
    """
    # Encode the Imaris channels information in xml.
    xml_root = et.Element('imaris_channels_information')
    xml_root.append(et.Comment('generated by SimpleITK'))

    for channel_information in channels_information_list:
        child = et.SubElement(xml_root, 'channel')
        current_field = et.SubElement(child, 'name')
        current_field.text = channel_information['name']
        current_field = et.SubElement(child, 'description')
        current_field.text = channel_information['description']
        # Set the color information
        if 'color' in channel_information:
            current_field = et.SubElement(child, 'color')
            color_info = channel_information['color']
        elif 'color_table' in channel_information:
            current_field = et.SubElement(child, 'color_table')
            color_info = channel_information['color_table']
        current_field.text = ', '.join([str(int(c*255 + 0.5)) for c in color_info])
        current_field = et.SubElement(child, 'range')
        current_field.text = '{0}, {1}'.format(channel_information['range'][0],
                                               channel_information['range'][1])
        current_field = et.SubElement(child, 'alpha')
        current_field.text = str(channel_information['alpha'])
        if 'gamma' in channel_information:  # Some images have gamma value some not
            current_field = et.SubElement(child, 'gamma')
            current_field.text = str(channel_information['gamma'])

    # Specify encoding as unicode to get a regular string, default is bytestring
    return et.tostring(xml_root, encoding='unicode')