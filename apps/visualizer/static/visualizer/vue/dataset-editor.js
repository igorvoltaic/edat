export default {
    name: 'dataset-editor',
    template: '#dataset-editor-template',
    delimiters: ['[[',']]'],
    components: {
        'dataset-editor-datarow': () => import(staticFiles + "vue/dataset-editor-datarow.js"),
    },
    props: ['result'],
    data() {
        return {
            filename: this.result.name,
            file_id: this.result.file_id,
            width: this.result.width,
            height: this.result.height,
            column_names: this.result.column_names,
            column_types: this.result.column_types,
            datatypes: ['number', 'float', 'datetime', 'boolean', 'string'],
            rows: this.result.datarows,
            edit: false,
        }
    },

    created: function () {
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
            this.column_types[index] = event.target.value;
        },

        onSave: function() {
            this.edit = true;
            fetch('/api/save', {
                method: 'POST',
                body: JSON.stringify({
                    name: this.filename,
                    file_id: this.file_id,
                    width: this.width,
                    height: this.height,
                    column_names: this.column_names,
                    column_types: this.column_types,
                    datarows: this.rows
                })
            })
            .then(response => response.json())
            .then(result => {
                router.push({
                    name: 'home',
                });
            });
        },
        onCancel: function() {
            this.edit = true;
            fetch(`/api/editor/${this.file_id}`, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(result => {
                router.push({
                    name: 'home',
                });
            })

        }
    },

}
