## Renson API

**GET** http://*[IP of the ventilation system]*/Reset  
This is reboot the device.  

**GET** http://*[IP of the ventilation system]*/FactoryReset
This will factory reset your device. !!Dangerous!!

**GET** http://*[IP of the ventilation system]*/JSON/ModifiedItems?wsn=150324488709  
This will get all modified data with their values.  

**GET** http://*[IP of the ventilation system]*/JSON/MetaData  
This will get all the possible fields and their metadata.  

**GET** http://*[IP of the ventilation system]*/JSON/Vars/*[name of the field]*?index0=*[dimension 1]*&index1=*[dimension 2]*&index2=*[dimension 3]*  
This wil get the value of one specific field.  
name of the field: the url encode fieldname that can be found in the /JSON/MetaData call  
dimension 1: First dimension in the list of dimensions that can be found in the /JSON/MetaData call  
dimension 2: Second dimension in the list of dimensions that can be found in the /JSON/MetaData call  
dimension 3: Thirth dimension in the list of dimensions that can be found in the /JSON/MetaData call  

**POST** http://*[IP of the ventilation system]*/JSON/Vars/*[name of the field]*?index0=*[dimension 1]*&index1=*[dimension 2]*&index2=*[dimension 3]*  
***Body***: { "Value":""}
This call will change the setting to a specific value
The body is a json with the key "Valeu" and the value of the field. Some settings has more configuration options.  

**POST** http://www.renson-app.com/endura_delta/firmware/check.php  
***Body***: {"a":"check", "name":"D_*[Version of current firmware]*.fuf"}
