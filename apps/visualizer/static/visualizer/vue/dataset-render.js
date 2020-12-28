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
                height: 600,
                width: 600,
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
            error: null
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
        resetDto: function() {
            document.querySelectorAll('.dropdown-default').forEach(elem => {
                elem.innerHTML = 'Select'
                elem.style.color = '#e1e1e1';
            })
            this.plotDto.params.x = null
            this.plotDto.params.y = null
            this.plotDto.params.hue = null
            this.plotDto.columns = []
            this.plotDto.height = 600
            this.plotDto.width = 600
        },
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
            this.error = null
            this.isLoading = true
            this.plotImgPath = null
            const path = '/api/render'
            let body = this.plotDto
            const doAjax = async () => {
                const response = await fetch(path, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });
                if (response.ok) {
                    const headers = await response.headers;
                    this.plotImgPath = headers.get('Content-Location')
                } else { 
                    const jVal = await response.json();
                    this.error = jVal.detail
                    return Promise.reject(jVal.detail); 
                }
            }
            doAjax().catch(console.log);       
        }
    },
}
