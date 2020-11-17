export default {
    template: '#dataset-list-template',
    components: {
        'dataset-list-item': () => import(staticFiles + "vue/dataset-list-item.js")
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
				this.datasets = result.datasets;
				// this.hasNext = result.has_next;
				// this.hasPrev = result.has_prev;
			})
        }
    }
}
