export default {
    name: 'dataset-visualizer',
    template: '#dataset-visualizer-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-visualizer-datarow': () => import(staticFiles + "vue/dataset-visualizer-datarow.js"),

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
