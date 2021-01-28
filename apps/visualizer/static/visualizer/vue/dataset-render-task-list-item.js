export default {
    name: 'dataset-render-tast-list-item',
    delimiters: ['[[',']]'],
    template: '#dataset-render-task-list-item-template',
    props: ['task'],
    data() {
        return {
            currentUser: currentUser,
            auth: auth
        }
    },
    methods: {
        formattedDate: function (date) {
            const d = new Date(date)
            function leadZero(n) {
              if(n <= 9){
                return "0" + n;
              }
              return n
            }
            return `${leadZero(d.getDate())}-${leadZero(d.getMonth())}-${d.getFullYear()} @ ${leadZero(d.getHours())}:${leadZero(d.getMinutes())}`
        },
        openDataset: function() {
            router.push({ name: 'dataset', params: { id: this.task.plot.dataset_id, task_result: this.task.result, task_args: this.task.plot } })
        },
    },
}
