export default {
    template: '#dataset-visualizer-template',
    components: {
        'dataset-list-item': () => import(staticFiles + "vue/dataset-list-item.js"),
    },
   data() {
        return {
            dataset: null,
        }
    },
    created: function () {
        this.fetchDataset(this.$route.params.id)
    },
    methods: {
        fetchDataset: function (dataset_id) {
			fetch(`/api/datasets/${dataset_id}`)
			.then(response => response.json())
			.then(result => {
				this.dataset = result;
			});
        },
    }
}
