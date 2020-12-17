export default {
    name: 'dataset-render',
    template: '#dataset-render-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-editor-datarow': () => import(staticFiles + "vue/dataset-editor-datarow.js"),
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
            plotImgPath: null
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
        selectItem: function (event, name) {
            const defaultText = event.target.parentElement.previousElementSibling
            const input = defaultText.parentElement.querySelector('input')
            defaultText.innerHTML = name
            defaultText.value = name
            defaultText.style.color = '#444'
            input.value = name
        },

        renderDataset: function () {
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
                id: this.id,
                x_axis: x_axis,
                y_axis: y_axis
            }
            fetch(path, {
                method: 'POST',
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(result => {
                this.plotImgPath = result.plot_img_path
            });

        }
    },
}
