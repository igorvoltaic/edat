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
                height: 2600,
                width: 2600,
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
        sleep: function (ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        resetDto: function() {
            document.querySelectorAll('.dropdown-default').forEach(elem => {
                elem.innerHTML = 'Select'
                elem.style.color = '#e1e1e1';
            })
            this.plotDto.params.x = null
            this.plotDto.params.y = null
            this.plotDto.params.hue = null
            this.plotDto.columns = []
            this.plotDto.height = 2600
            this.plotDto.width = 2600
        },
        updateColumns: function() {
            let selectedColumns = []
            let x = document.querySelector('input[name="x"]').value
            let y = document.querySelector('input[name="y"]').value
            selectedColumns.push(x)
            if (!selectedColumns.includes(y)) {
                selectedColumns.push(y)
            }
            this.plotDto.columns = selectedColumns
        },
        getRenderTask: function (path) {
            const doAjax = async () => {
                const response = await fetch(path, {
                    method: 'GET',
                });
                const result = await response.json();
                if (response.ok && result.result) {
                    this.plotImgPath = `/${result.result}`
                } else if (response.status == 400)  { 
                    this.error = result.detail
                    return Promise.reject(result.detail); 
                } else if (response.status == 404)  { 
                    this.error = 'Plot not found'
                    return Promise.reject(result.detail); 
                } 
            }
            doAjax().catch(console.log);       
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
                if (response.status == 202) {
                    const headers = await response.headers;
                    const status_path = headers.get('Content-Location')
                    while (!this.plotImgPath) {
                        if (this.error) {
                            break
                        }
                        this.getRenderTask(status_path)
                        await this.sleep(5000)
                    }
                } else if (response.status == 307) {
                    const headers = await response.headers;
                    router.push({
                        name: 'login',
                    });
                } else if (response.status == 303) {
                    const headers = await response.headers;
                    this.plotImgPath = headers.get('Content-Location')
                } else { 
                    const result = await response.json();
                    this.error = result.detail
                    return Promise.reject(result.detail); 
                }
            }
            doAjax().catch(console.log);       
        }
    },
}
