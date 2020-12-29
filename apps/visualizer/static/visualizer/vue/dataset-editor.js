export default {
    name: 'dataset-editor',
    template: '#dataset-editor-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-editor-datarow': () => import(staticFiles + "vue/dataset-editor-datarow.js"),
        'dropdown-select': () => import(staticFiles + "vue/dropdown-select.js"),
    },
    props: ['id', 'result', 'new_dataset'],
    data() {
        return {
            file_id: null,
            datasetInfo: {
                csv_dialect: {
                    delimiter: null,
                    quotechar: null,
                    has_header: null,
                    start_row: "",
                }
            },
            datatypes: ['number', 'float', 'datetime', 'boolean', 'string'],
            delimiters: [
                { name: 'comma', value: ',' },
                { name: 'semicolon', value: ';' },
                { name: 'colon', value: ':' },
                { name: 'space', value: ' ' },
                { name: 'tab', value: '\t' },
            ],
            quotechars: [
                { name: 'singlequote', value: "'" },
                { name: 'doublequote', value: '"' },
            ],
            has_header: [
                { name: 'true', value: true },
                { name: 'false', value: false }
            ],
            rows: null,
            edit: false,
            isHidden: true,
        }
    },

    created: function () {
        // fetch dataset
        let path = null
        if (!this.id) {
            path = `/api/upload/${this.$route.query.file_id}`
        } else {
            path = `/api/dataset/${this.id}`
        }
        fetch(path)
        .then(response => {
            if (!response.ok) {
                throw new Error('Dataset not found');
            }
            return response.json()
        })
        .then(result => {
            this.datasetInfo = result
            this.rows = result.datarows
        })
        .catch(ex => {
            console.log(ex.message);
        })

        window.addEventListener("beforeunload", this.preventNav);
        this.$once("hook:beforeDestroy", () => {
          window.removeEventListener("beforeunload", this.preventNav);
        })
    },

    beforeRouteLeave(to, from, next) {
        if (!this.edit) {
            if (!window.confirm("Leave without saving?")) {
                return;
            }
        }
        next();
    },

    methods: {
        preventNav: function(event) {
            event.preventDefault()
            event.returnValue = ""
        },

        onChangeType: function(idx, item) {
            this.datasetInfo.column_types[idx] = item
        },

        onSave: function() {
            this.edit = true;
            const comment = document.querySelector('#comment').value
            let body = this.datasetInfo
            let path = null
            let method = null
            if (!this.id) {
                path= '/api/dataset'
                method = 'POST'
            } else {
                path = `/api/dataset/${this.id}`
                method = 'PUT'
            }
            body.comment = comment
            fetch(path, {
                method: method,
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(() => {
                router.push({
                    name: 'home',
                });
            });
        },

        reReadFile: function() {
            this.edit = true;
            let body = this.datasetInfo.csv_dialect
            let path = null
            if (!this.id) {
                path = `/api/upload/${this.datasetInfo.file_id}`
            } else {
                path = `/api/dataset/${this.id}`
            }
            if (!this.datasetInfo.csv_dialect.start_row || this.datasetInfo.csv_dialect.start_row.length < 1) {
                body.start_row = null
            }
            fetch(path, {
                method: 'POST',
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(result => {
                this.datasetInfo.width = result.width
                this.datasetInfo.column_names = result.column_names
                this.datasetInfo.column_types = result.column_types
                this.datasetInfo.csv_dialect.delimiter = result.csv_dialect.delimiter
                this.datasetInfo.csv_dialect.quotechar = result.csv_dialect.quotechar
                this.datasetInfo.csv_dialect.has_header = result.csv_dialect.has_header
                this.datasetInfo.csv_dialect.start_row = result.csv_dialect.start_row
                this.rows = result.datarows
            });
         },

        onCancel: function() {
            this.edit = true;
            if (!this.id) {
                fetch(`/api/upload/${this.datasetInfo.file_id}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(() => {
                    router.push({
                        name: 'home',
                    });
                });
            } else {
                router.push({
                    name: 'home',
                });
            }
        }

    },
}
