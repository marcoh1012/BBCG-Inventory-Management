# BBCG-Inventory-Management
Inventory Management App for BBCG <br>
Deployment: https://bbcg-inventory-management.herokuapp.com/ <br>
View ReadMe File for login details

### Barcode Generator API:
https://barcodes4.me/apidocumentation

### Scanning API:
https://serratus.github.io/quaggaJS/

### Goal:
The Goal of this app is to keep better track of the inventory and material used for a granite counter top fabrication business.
The data is collected from the user on a daily basis and is used to genereate weekly reports about the jobs and materials used that week. The data can later be used to calculate wasted material and much more. 

### Key Features:
<ul>
  <li>Auto Generated Barcode using Slab ID</li>
  <li>Scan Barcode with Camera</li>
  <li>View All Inventory and search/sort</li>
  <li>View All Jobs and search/sort</li>
  <li>Add Slabs and Jobs </li>
  <li> Generate Report for the Week </li>
</ul>


This deployment is just a prototype version for the app. You can check it out using one of the 4 Type of accounts:

##### Admin:
-admins have full control of the app.<br>
username: admin<br>
password: catdog123

##### Reciever:
-recievers can only recieve(add) slabs and print the labels for them <br>
username: reciever <br>
password: catdog123

##### Fabricator:
-fabricators can only update the slab that is cut with hoe much and what job it was used on by scanning the barcode <br>
username: fabricator <br>
password: catdog123

##### Office:
-office/secretaries has almost full access except for a few items only available to admins <br>
username: office <br>
password: catdog123


### Process
<ol>
  <li>Reciever: Recieve Slab and label it</li>
  <li>Repeat Step 1 for every Slab recieved during the week</li>
  <li>Office: Add Job and information</li>
  <li>Repeat Step 3 for each job during the week</li>
  <li>Fabricator: Scan slab and cut slab</li>
  <li>Update how much material was used with the job name</li>
  <li>Repeat steps 5 and 6 for each slab cut</li>
  <li>View report for the week </li>
<ol>
  <br><br>
  
  App Created Using: Python, HTML, Bootstrap, Flask, CSS, Javascript
