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
            filename: this.result.filename,
            file_id: this.result.file_id,
            column_names: this.result.column_names,
            column_types: this.result.column_types,
            datatypes: ['number', 'float', 'datetime', 'boolean', 'string'],
            rows: this.result.datarows,
        }
    },

    created: function () {
        window.addEventListener("beforeunload", this.preventNav);
        this.$once("hook:beforeDestroy", () => {
          window.removeEventListener("beforeunload", this.preventNav);
        })
    },

    beforeRouteLeave(to, from, next) {
        if (!window.confirm("Leave without saving?")) {
            return;
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
            fetch('/api/save_dataset', {
                method: 'POST',
                body: JSON.stringify({
                    name_info: this.filename,
                    tmpfile: this.file_id,
                    column_names: this.column_names,
                    column_types: this.column_types,
                    rows: this.rows,
                })
            })
            .then(response => response.json())
            .then(result => {
                // router.push({
                //     name: 'home',
                // });
            });
        },
        onCancel: function() {

        }
    },

}
