export default {
    name: 'dataset-editor',
    template: '#dataset-editor-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-editor-datarow': () => import(staticFiles + "vue/dataset-editor-datarow.js"),
    },
    props: ['result', 'new_dataset'],
    data() {
        return {
            file_id: null,
            id: null,
            datasetInfo: {
                name: this.result.name,
                timestamp: this.result.timestamp,
                width: this.result.width,
                height: this.result.height,
                column_names: this.result.column_names,
                column_types: this.result.column_types,
                comment: this.result.comment,
                csv_dialect: {
                    delimiter: this.result.csv_dialect.delimiter,
                    quotechar: this.result.csv_dialect.quotechar,
                    has_header: this.result.csv_dialect.has_header,
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
            rows: this.result.datarows,
            edit: false,
            isHidden: true,
        }
    },

    created: function () {
        if (this.new_dataset) {
            this.file_id = this.result.file_id
        } else {
            this.id = this.result.id
        }
        this.file_id = this.result.file_id,
        this.id = this.result.id,
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

        onChangeType: function(event, index) {
            this.datasetInfo.column_types[index] = event.target.value;
        },

        onSave: function() {
            this.edit = true;
            const comment = document.querySelector('#comment').value
            let body = this.datasetInfo
            let path = null
            let method = null
            if (this.new_dataset) {
                body.file_id = this.result.file_id
                path= '/api/create'
                method = 'POST'
            } else {
                body.id = this.result.id
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
            if (this.new_dataset) {
                path = `/api/reread?file_id=${this.file_id}`
            } else {
                path = `/api/reread/${this.id}`
            }
            body.delimiter = document.querySelector('#csv-delimiter').value
            body.quotechar = document.querySelector('#csv-quotechar').value
            body.has_header = document.querySelector('#csv-has-header').value
            if (body.start_row = document.querySelector('#csv-start-row').value.length > 0) {
                body.start_row = document.querySelector('#csv-start-row').value
            } else {
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
                this.rows = result.datarows
            });
         },

        onCancel: function() {
            this.edit = true;
            if (this.new_dataset) {
                fetch(`/api/create/${this.file_id}`, {
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
