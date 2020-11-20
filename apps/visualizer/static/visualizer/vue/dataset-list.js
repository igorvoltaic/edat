export default {
    template: '#dataset-list-template',
    components: {
        'dataset-list-item': () => import(staticFiles + "vue/dataset-list-item.js"),
    },
   data() {
        return {
            pageNum: 1,
            datasets: null,
            hasNext: null,
            hasPrev: null,
            auth: auth
        }
    },
    created: function () {
        this.fetchDatasets(this.pageNum)
    },
    methods: {
        fetchDatasets: function (p) {
			fetch(`/api/datasets?page=${p}`)
			.then(response => response.json())
			.then(result => {
				this.datasets = result; // add pagination
			});
        },
        showFilename: function () {
            const fileInput = document.querySelector('#upload-csv-file')
            document.querySelector("#upload-csv-file-label").innerHTML = fileInput.files[0].name
        },
    }
}
