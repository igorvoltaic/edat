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

        onSaveDialect: function() {
            this.datasetInfo.csv_dialect.delimiter = document.querySelector('#csv-delimiter').value;
            this.datasetInfo.csv_dialect.quotechar = document.querySelector('#csv-quotechar').value;
            if (document.querySelector('#csv-has-header').value === "false") {
                this.datasetInfo.csv_dialect.has_header = false
            } else {
                this.datasetInfo.csv_dialect.has_header = true
            }
        },

        onCreate: function() {
            this.edit = true;
            const comment = document.querySelector('#comment').value
            let body = this.datasetInfo
            body.file_id = this.result.file_id
            body.comment = comment
            fetch('/api/create', {
                method: 'POST',
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(() => {
                router.push({
                    name: 'home',
                });
            });
        },

        onSave: function() {
            this.edit = true;
            const comment = document.querySelector('#comment').value
            let body = this.datasetInfo
            body.id = this.result.id
            body.comment = comment
            fetch(`/api/datasets/${this.id}`, {
                method: 'PUT',
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
            const comment = document.querySelector('#comment').value
            let body = this.datasetInfo
            body.file_id = this.result.file_id
            body.comment = comment
            fetch('/api/create', {
                method: 'POST',
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(() => {
                router.push({
                    name: 'home',
                });
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
