export default {
    name: 'dataset-render-task-list',
    delimiters: ['[[',']]'],
    template: '#dataset-render-task-list-template',
    components: {
        'dataset-render-task-list-item': () => import(staticFiles + "vue/dataset-render-task-list-item.js"),
    },
    data() {
        return {
            pageNum: 1,
            tasks: [],
            hasNext: null,
            hasPrev: null,
            auth: auth,
            numPages: null,
            error: null,
        }
    },
    created: function () {
        this.fetchTasks(this.pageNum);
    },
    methods: {
        isActivePage: function(n) {
            if (this.pageNum !== n) {
                return false
            }
            return true
        },
        fetchTasks: function (p, q = false) {
            let searchString = ''
            if (q) {
                searchString = '&query=' + document.querySelector('#search').value
            }
            fetch(`/api/render?page=${p}${searchString}`)
            .then(response => response.json())
            .then(result => {
                this.tasks = result.tasks;
                this.hasNext = result.has_next;
                this.hasPrev = result.has_prev;
                this.numPages = result.num_pages;
                this.pageNum = result.page_num;
            });
        },
    }
}
