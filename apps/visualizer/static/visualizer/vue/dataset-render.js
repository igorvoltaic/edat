export default {
    name: 'dataset-render',
    template: '#dataset-render-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-editor-datarow': () => import(staticFiles + "vue/dataset-editor-datarow.js"),
        'dropdown-select': () => import(staticFiles + "vue/dropdown-select.js"),
    },
    props: ['id'],
    data() {
        return {
            datasetInfo: {
                name: null,
                column_names: null,
                column_types: null,
                comment: null,
            },
            rows: [],
            plotDto: {
                dataset_id: this.id,
                height: null,
                width: null,
                plot_type: 'scatter',
                params: {
                    x: null,
                    y: null,
                    hue: null,
                },
                columns: [],
            },
            plot_types: [ 
                "strip", "swarm", "box", "violin",
                "boxen", "point", "bar", "count", "scatter",
                "line", "hist", "kde", "ecdf",
            ],
            plotImgPath: null,
            isLoading: false,
        };
    },
    created: function () {
        fetch(`/api/dataset/${this.id}`)
        .then(response => {
            if (response.status !== 200) {
                throw new Error('Dataset not found');
            }
            return response.json()
        })
        .then(result => {
            this.datasetInfo.name = result.name
            this.datasetInfo.column_names = result.column_names
            this.datasetInfo.column_types = result.column_types
            this.rows = result.datarows
        })
        .catch(ex => {
            console.log(ex.message);
        })

    },

    methods: {
        updateHue: function() {
            let hueCols = []
            let x = document.querySelector('input[name="x"]').value
            let y = document.querySelector('input[name="y"]').value
            hueCols.push(x)
            if (!hueCols.includes(y)) {
                hueCols.push(y)
            }
            this.plotDto.columns = hueCols
        },
        renderDataset: function () {
            this.isLoading = true
            this.plotImgPath = null
            const x_axis = document.querySelector('input[name="x_axis"]').value
            const y_axis = document.querySelector('input[name="y_axis"]').value
            const cnames = this.datasetInfo.column_names
            const correctInput = cnames.includes(x_axis || y_axis) ? true : false
            if (!correctInput) {
                console.log('Must provide valid column names');
                return;
            }
            const path = '/api/render'
            let body = {
            }
            fetch(path, {
                method: 'POST',
                body: JSON.stringify(body)
            })
            .then(response => response.headers)
            .then(result => {
                this.plotImgPath = result.plot_img_path
            });

        }
    },
}
