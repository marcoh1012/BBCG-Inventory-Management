### *Capstone Project Proposal - BBCG Inventory Management*

##### Goal:

​		The purpose of this project is to keep better inventory and tracking of all material used. The data from this will help obtain more accurate data on how much material is used per job and how much of it is going to waste. The app will give a vast amount of other useful data about the materials used, jobs fabricated and installed. 

##### Target Audience:

​		This app is targeted specifically for Best Buy Carpet & Granite (BBCG) to improve their inventory management for the granite department. However it can be modified in the future to apply to more companies that do not have to be related to granite. 

##### Data:

​		All data will be gathered from the user input with the help of some API’s to make this process easier.

##### API's:

- [barcode4me](https://barcodes4.me/)- generate a barcode to print and label each slab of material
  - barcode will store the slab id composed of (vendor + lot number + slab number)
- [scandit](https://docs.scandit.com/stable/web/) - allows to scan the barcode from the web browser without having to upload a picture making easier and more efficient

##### Schema:

![Database Schema](/pictures/DatabaseDiagram.jpeg)

##### Possible Issues/Functionality:

​		More functionality and Data may need to be added as the app is used. There are scenarios that may occur and have not been taken into account

##### Users:

​		Four Types of Users: Admin, Receiver, Fabricator, & Templator. User Flow Diagram Shown below of each type of user.



Admin:

![Admin](/pictures/Admin.jpeg)

Receiver:

![Receiver](/pictures/Receiver.jpeg)

Fabricator: 

 ![fabricator](/pictures/fabricator.jpeg)

Templator:

 ![Templator](/pictures/Templator.jpeg)



