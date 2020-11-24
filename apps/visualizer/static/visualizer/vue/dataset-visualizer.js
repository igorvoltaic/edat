export default {
    name: 'dataset-visualizer',
    template: '#dataset-visualizer-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-visualizer-datarow': () => import(staticFiles + "vue/dataset-visualizer-datarow.js"),

    },
    data() {
        return {
            dataset: [],
            column_names: [],
            column_types: [],
            datatypes: ['number', 'float', 'datetime', 'boolean', 'string'],
            rows: [],
        }
    },
    created: function () {
        this.fetchDataset(this.$route.params.id)
        $('.tag.example .ui.dropdown')
        .dropdown({
            allowAdditions: true
        });
    },
    methods: {
        fetchDataset: function (dataset_id) {
			fetch(`/api/datasets/${dataset_id}`)
			.then(response => response.json())
			.then(result => {
				this.dataset = result;
                this.column_names = result.file_info.column_names;
                this.column_types = result.file_info.column_types;
                this.rows = result.file_info.datarows;
			});
        },
    }
}
