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
            fetch(`/api/datasets?page=${p}${searchString}`)
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
            var data = new FormData()
            const fileInput = document.querySelector('#upload-csv-file');
            data.append('file', fileInput.files[0]);
            fetch('/api/datasets', {
                method: 'POST',
                body: data,
            })
            .then(response => {
                if (response.status !== 200) {
                    throw new Error('File upload error')
                }
                return response.json()
            })
            .then(result => {
                router.push({
                    name: 'editor',
                    params: {
                        result: result,
                        new_dataset: true,
                    },
                });
            })
            .catch(ex => {
                console.log(ex.message);
                this.error = ex.message + ": please provide .csv file with at least two columns and two rows";
            })

            // Prevent default submission
            return false;
        },
    }
}
