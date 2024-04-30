document.querySelector('.logout-btn').addEventListener('click', function () {
            window.location.href = 'login';
        });
        //  search
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
        // search in MongoDB database
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
        // search Mysql database
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


        // Post
        async function postData(url = "", data = {}) {
            // Default options are marked with *
            const response = await fetch(url, {
                method: "POST", // *GET, POST, PUT, DELETE, etc.
                mode: "cors", // no-cors, *cors, same-origin
                cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
                credentials: "same-origin", // include, *same-origin, omit
                headers: {
                    "Content-Type": "application/json",
                    // 'Content-Type': 'application/x-www-form-urlencoded',
                },
                redirect: "follow", // manual, *follow, error
                referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
                body: JSON.stringify(data), // body data type must match "Content-Type" header
            });
            return response.json(); // parses JSON response into native JavaScript objects
        }
        // show tables in mysql
        function showMysqlTables(dbName) {
            fetch(`/get-tables/${dbName}`)
                .then(response => response.json())
                .then(data => {
                    const detailPanel = document.querySelector('.database-details');
                    detailPanel.innerHTML = `<h3>Tables in ${dbName}</h3><ul>`;
                    data.forEach(table => {
                        detailPanel.innerHTML += `<li onclick="showData('${table}')">${table}</li>`;
                    });
                    detailPanel.innerHTML += '</ul>';
                });
        }

        // show users data in mysql
        function showData(tableName) {
            console.log(tableName)
            postData("/userListMysql", {
                pageNum: 1,
                pageSize: 999
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
        // add user in mysql
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
        // update username
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
        // update user type
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
        // general update
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
        // general delete
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


        // ----------------------------------------------
// ----------------------------------------------

        // MongoDB show user data tables
        function showMongoData(tableName) {
            console.log(tableName)
            postData("/userListMongoDB", {
                pageNum: 1,
                pageSize: 999
            }).then((data) => {
                console.log(data);
                const detailPanel = document.querySelector('.database-data');
                let isAdmin = localStorage.getItem('type')
                if (isAdmin === 'administrator') {
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
        // MongoDB add user
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
                        alert('user data added suffessful!')
                    }, 1000)
                })
            }

        }
        // update username
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
        // update user type
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