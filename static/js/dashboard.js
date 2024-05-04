document.querySelector('.logout-btn').addEventListener('click', function () {
            localStorage.removeItem('type');
            window.location.href = 'login';
        });
        document.querySelector('.search-btn').addEventListener('click', function () {

            const searchValue = document.querySelector('.search-bar').value.toLowerCase();
            let found = false;
            const listItems = document.querySelectorAll('.database-list li');
            listItems.forEach(item => {
                if (item.textContent.toLowerCase().includes(searchValue)) {
                    item.style.display = '';
                    found = true;
                } else {
                    item.style.display = 'none';
                }
            });
            if (!found) {
                document.querySelector('.database-details').innerHTML = `
               <h3>Database Details</h3>
               <p>No Valid Database Selected!</p>`;
            }
        });
        document.getElementById('MongoDB-database').addEventListener('click', function () {
            fetch('/get_data_list', {
                    method: "POST"
                })
                .then(response => response.json())
                .then(data => {
                    const detailPanel = document.querySelector('.database-details');
                    detailPanel.innerHTML = '<h3>MongoDb data</h3><ul>';
                    data.data.forEach(db => {
                        detailPanel.innerHTML += `<li onclick="showMongoData('${db}')">${db}</li>`;
                    });
                    detailPanel.innerHTML += '</ul>';
                });
        });
        document.getElementById('mysql-database').addEventListener('click', function () {
            fetch('/get-databases')
                .then(response => response.json())
                .then(data => {
                    const detailPanel = document.querySelector('.database-details');
                    detailPanel.innerHTML = '<h3>MySQL Databases</h3><ul>';
                    data.forEach(db => {
                        detailPanel.innerHTML +=
                            `<li onclick="showMysqlTables('${db}')">${db}</li>`;
                    });
                    detailPanel.innerHTML += '</ul>';
                });
        });

        async function postData(url = "", data = {}) {
            const response = await fetch(url, {
                method: "POST",
                mode: "cors",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                },
                redirect: "follow",
                referrerPolicy: "no-referrer",
                body: JSON.stringify(data),
            });
            return response.json();
        }
        // show tables in mysql
        function showMysqlTables(dbName) {
            fetch(`/get-tables/${dbName}`)
                .then(response => response.json())
                .then(data => {
                    const detailPanel = document.querySelector('.database-details');
                    detailPanel.innerHTML = `<h3>Tables in ${dbName}</h3><ul>`;
                    data.forEach(table => {
					    if(table == "users"){
						 detailPanel.innerHTML += `<li onclick="showData('${table}')">${table}</li>`;
						}else if(table == "house_rent_dataset"){
						 detailPanel.innerHTML += `<li onclick="showHouseData('${table}')">${table}</li>`;
						}else{
                            detailPanel.innerHTML += `<li onclick="showNormalData('${table}', '${dbName}')">${table}</li>`;
                        }

                    });
                    detailPanel.innerHTML += '</ul>';
                });
        }

        function showData(tableName) {
            console.log(tableName)
            postData("/userListMysql", {
                pageNum: 1,
                pageSize: 999,
                table:tableName
            }).then((data) => {
                console.log(data);
                const detailPanel = document.querySelector('.database-data');
                let isAdmin = localStorage.getItem('type')
                if (isAdmin === 'administrator') {
                    detailPanel.innerHTML = `
                <h3>MysqlData in ${tableName}</h3>
                <button onClick="addMysqlUser('${tableName}')">add</button>
                <ul>`;
                    data.data.forEach((table, index) => {

                        detailPanel.innerHTML += `
                        <li class="item">
                            <div class="left">
                                userid：${table.id}  username：${table.username}  type：${table.type}    
                            </div>
                            <div class="right">
                                <button  onClick="deleteMysqlUser('${table.id}','${index}','${tableName}')">delete</button>
              
                                <button  onClick="editMysqlUserName('${table.id}','${table.username}','${table.type}','${tableName}')">edit username</button>
                                <button  onClick="editMysqlUserType('${table.id}','${table.username}','${table.type}','${tableName}')">edit type</button>
                            </div>
                        </li>
                        `;

                    });
                    detailPanel.innerHTML += '</ul>';
                } else {
                    detailPanel.innerHTML = `
                <h3>MysqlData in ${tableName}</h3>

                <ul>`;
                    data.data.forEach((table, index) => {

                        detailPanel.innerHTML += `
                        <li class="item">
                            <div class="left">
                                userid：${table.id}  username：${table.username}  type：${table.type}    
                            </div>
                            
                        </li>
                        `;

                    });
                    detailPanel.innerHTML += '</ul>';
                }

            });

        }
        function addMysqlUser(tableName) {
            let params = {

                username: '',
                password: '',
                type: ''
            }
            params.username = prompt('insert username', '')

            params.password = prompt('insert password', '')
            params.type = prompt('insert tpye', '')
            if (params.username && params.password && params.type) {
                postData("/addUserMysql", params).then((data) => {

                    showData(tableName)
                    setTimeout(() => {
                        alert('user data added suffessful!')
                    }, 1000)
                })
            }

        }
        function editMysqlUserName(id, username, type, tableName) {

            let params = {
                id,
                username,
                type
            }
            params.username = prompt('insert new username', username)
            if (!params.username) return
            editMysqlUser(params, tableName)
        }
        function editMysqlUserType(id, username, type, tableName) {
            let params = {
                id,
                username,
                type
            }
            params.type = prompt('insert tpye', type)
            if (!params.type) return
            editMysqlUser(params, tableName)
        }
        function editMysqlUser(params, tableName) {
            console.log()
            postData("/updateUser", params).then((data) => {
                console.log(data)
                showData(tableName)
                setTimeout(() => {
                    alert('user data updated successful!')
                }, 1000)
            })
        }
        function deleteMysqlUser(id, index, tableName) {
            postData("/deleteUser", {
                id: id
            }).then((data) => {
                console.log(data)
                showData(tableName)
                setTimeout(() => {
                    alert('user data deleted successful!')
                }, 1000)
            })
        }

        function showMongoData(tableName) {
            console.log(tableName)
            postData("/userListMongoDB", {
                pageNum: 1,
                pageSize: 999
            }).then((data) => {
                console.log(data);
                const detailPanel = document.querySelector('.database-data');
                let isAdmin = localStorage.getItem('type')
                if (isAdmin === 'administrator') { //administrator
                    detailPanel.innerHTML = `
                <h3>MongoDBData in ${tableName}</h3>
                <button onClick="addMongoDBUser('${tableName}')">add user</button>
                <ul>`;
                    data.data.forEach((table, index) => {

                        detailPanel.innerHTML += `
                        <li class="item" style="background-color: #ddffdd;">
                            <div class="left">
                                userid：${table.id}  username：${table.username}  type：${table.type}    
                            </div>
                            <div class="right">
                                <button  onClick="deleteMongoDBUser('${table.id}','${index}','${tableName}')">delete</button>
                                <button  onClick="editMongoDBUserName('${table.id}','${table.username}','${table.type}','${tableName}')">edit username</button>
                                <button  onClick="editMongoDBUserType('${table.id}','${table.username}','${table.type}','${tableName}')">edit tpye</button>
                            </div>
                        </li>
                        `;


                    });
                    detailPanel.innerHTML += '</ul>';
                } else {
                    detailPanel.innerHTML = `
                <h3>MongoDBData in ${tableName}</h3>
            
                <ul>`;
                    data.data.forEach((table, index) => {

                        detailPanel.innerHTML += `
                        <li class="item" style="background-color: #ddffdd;">
                            <div class="left">
                                userid：${table.id}  username：${table.username}  tpye：${table.type}    
                            </div>
                    
                        </li>
                        `;


                    });
                    detailPanel.innerHTML += '</ul>';
                }

            });

        }
        function addMongoDBUser(tableName) {
            let params = {

                username: '',
                password: '',
                type: ''
            }
            params.username = prompt('insert username', '')

            params.password = prompt('insert password', '')
            params.type = prompt('insert type', '')
            if (params.username && params.password && params.type) {
                postData("/addUserMongoDB", params).then((data) => {

                    showMongoData(tableName)
                    setTimeout(() => {
                        alert('user data added successful!')
                    }, 1000)
                })
            }

        }

        function showHouseData(tableName) {
            console.log(tableName);
            postData("/houseList", {
                pageNum: 1,
                pageSize: 999
            }).then((data) => {
                console.log(data);
                const detailPanel = document.querySelector('.database-data');
                let isAdmin = localStorage.getItem('type');
                if (isAdmin === 'administrator') { //administrator
                    console.log(isAdmin);
                    detailPanel.innerHTML = `
                <h3>MySQL Data in ${tableName}</h3>
                <button onClick="addHouse()">Add House</button>
                <ul>`;
                    data.data.forEach((house, index) => {
                        detailPanel.innerHTML += `
                        <li class="item">
                            <div class="left">
                                HouseID: ${house.HouseID} PostedOn: ${house.PostedOn}, BHK: ${house.BHK}, Rent: ${house.Rent}, Size:${house.Size}, City:${house.City}, FurnishingStatus:${house.FurnishingStatus} 
                            </div>
                            <div class="right">
                                <button onClick="deleteHouse('${house.HouseID}','${index}')">Delete</button>
                                <button onClick="editHouse('${house.HouseID}', '${house.PostedOn}', '${house.BHK}', '${house.Rent}', '${house.Size}', '${house.City}', '${house.FurnishingStatus}')">Edit</button>
                            </div>
                        </li>`;
                    });
                    detailPanel.innerHTML += '</ul>';
                } else {
                    console.log(isAdmin);
                    detailPanel.innerHTML = `
                <h3>MySQL Data in ${tableName}</h3>
                <ul>`;
                    data.data.forEach((house, index) => {
                        detailPanel.innerHTML += `
                        <li class="item">
                            <div class="left">
                                HouseID: ${house.HouseID} PostedOn: ${house.PostedOn}, BHK: ${house.BHK}, Rent: ${house.Rent}, Size:${house.Size}, City:${house.City}, FurnishingStatus:${house.FurnishingStatus}
                            </div>
                        </li>`;
                    });
                    detailPanel.innerHTML += '</ul>';
                }
            });
        }

        function addHouse() {
            let params = {
                HouseID:parseInt(prompt('Enter HouseID', '')),
                PostedOn: prompt('Enter posted date', ''),
                BHK: parseInt(prompt('Enter BHK', '')),
                Rent: parseFloat(prompt('Enter rent', '')),
                Size: parseInt(prompt('Enter size', '')),
                City: prompt('Enter city', ''),
                FurnishingStatus: prompt('Enter furnishing status', '')
            };
            if (params.PostedOn && params.City && !isNaN(params.BHK) && !isNaN(params.Rent) && !isNaN(params.Size)) {
                postData("/addHouse", params).then((data) => {
                    showHouseData('house_rent_dataset');
                    setTimeout(() => {
                        alert('House data added successfully!');
                    }, 1000);
                });
            }
        }

        function editHouse(HouseID, PostedOn, BHK, Rent, Size, City, FurnishingStatus) {
            let params = {
                HouseID: HouseID,
                PostedOn: prompt('Modify posted date', PostedOn),
                BHK: parseInt(prompt('Modify BHK', BHK)),
                Rent: parseFloat(prompt('Modify rent', Rent)),
                Size: parseInt(prompt('Modify size', Size)),
                City: prompt('Modify city', City),
                FurnishingStatus: prompt('Modify furnishing status', FurnishingStatus)
            };
            if (params.PostedOn && params.City && !isNaN(params.BHK) && !isNaN(params.Rent) && !isNaN(params.Size)) {
            postData("/updateHouse", params).then((data) => {
                showHouseData('house_rent_dataset');
                setTimeout(() => {
                    alert('House data updated successfully!');
            }, 1000);
            });
        }
    }

        function deleteHouse(HouseID, index) {
            postData("/deleteHouse", {
                HouseID: HouseID
            }).then((data) => {
                console.log(data);
                showHouseData('house_rent_dataset');
                setTimeout(() => {
                    alert('House data deleted successfully!');
                }, 1000);
            });
        }

        function editMongoDBUserName(id, username, type, tableName) {

            let params = {
                id,
                username,
                type
            }
            params.username = prompt('insert new username', username)
            if (!params.username) return
            editMongoDBUser(params, tableName)
        }
        function editMongoDBUserType(id, username, type, tableName) {
            let params = {
                id,
                username,
                type
            }
            params.type = prompt('insert new user tpye', type)
            if (!params.type) return
            editMongoDBUser(params, tableName)
        }

        function editMongoDBUser(params, tableName) {
            console.log()
            postData("/updateUserMongoDB", params).then((data) => {
                console.log(data)
                showMongoData(tableName)
                setTimeout(() => {
                    alert('user data updated successful!')
                }, 1000)
            })
        }

        function deleteMongoDBUser(id, index, tableName) {
            postData("/deleteUserMongoDB", {
                id: id
            }).then((data) => {
                console.log(data)
                showMongoData(tableName)
                setTimeout(() => {
                    alert('user data deleted successful!')
                }, 1000)
            })
        }

        function showNormalData(tableName, dbName) {
            console.log(tableName);
            postData("/NormalList", {
                pageNum: 1,
                pageSize: 999,
                tableName: tableName,
                dbName: dbName
            }).then((data) => {
                console.log(data);
                const detailPanel = document.querySelector('.database-data');
                detailPanel.innerHTML = `<h3>MySQL Data in ${tableName}</h3><ul>`;
                data.data.forEach((item, index) => {
                    let itemDetails = Object.keys(item).map(key => `${key}: ${item[key]}`).join(', ');
                    detailPanel.innerHTML += `<li class="item"><div class="left">${itemDetails}</div></li>`;
                });
                detailPanel.innerHTML += '</ul>';
            });
        }
