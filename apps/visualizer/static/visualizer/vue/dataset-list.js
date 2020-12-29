export default {
    name: 'dataset-list',
    delimiters: ['[[',']]'],
    template: '#dataset-list-template',
    components: {
        'dataset-list-item': () => import(staticFiles + "vue/dataset-list-item.js"),
    },
    data() {
        return {
            pageNum: 1,
            datasets: [],
            hasNext: null,
            hasPrev: null,
            auth: auth,
            numPages: null,
            error: null,
        }
    },
    created: function () {
        this.fetchDatasets(this.pageNum);
    },
    methods: {
        isActivePage: function(n) {
            if (this.pageNum !== n) {
                return false
            }
            return true
        },
        fetchDatasets: function (p, q = false) {
            let searchString = ''
            if (q) {
                searchString = '&query=' + document.querySelector('#search').value
            }
            fetch(`/api/dataset?page=${p}${searchString}`)
            .then(response => response.json())
            .then(result => {
                this.datasets = result.datasets;
                this.hasNext = result.has_next;
                this.hasPrev = result.has_prev;
                this.numPages = result.num_pages;
                this.pageNum = result.page_num;
            });
        },
        addFilename: function () {
            const fileInput = document.querySelector('#upload-csv-file')
            document.querySelector("#upload-csv-file-label").innerHTML = fileInput.files[0].name
        },
        addDataset: function() {
            this.error = null
            let data = new FormData()
            const fileInput = document.querySelector('#upload-csv-file');
            data.append('file', fileInput.files[0]);
            const path = '/api/upload'
            const doAjax = async () => {
                const response = await fetch(path, {
                    method: 'POST',
                    body: data,
                });
                if (response.ok) {
                    const headers = response.headers;
                    let file_id = headers.get('Location')
                    router.push({
                        name: "editor",
                        query: {
                            file_id,
                        },
                    });
                } else { 
                    const jVal = await response.json();
                    this.error = jVal.detail + ": please provide .csv file with at least two columns and two rows";
                    return Promise.reject(jVal.detail); 
                }
            }
            doAjax().catch(console.log);       
        },
    }
}
