export default {
    name: 'dropdown-select',
    template: '#dropdown-select-template',
    delimiters: ['[[',']]'],
    props: ['items', 'name', 'selected' ],
    data() {
        return {
            isActive: false,
            isCreated: true
        }
    },
    methods: {
        classToggle: function(event) {
            const menu = event.target.parentElement.querySelector('.dropdown-menu')
            menu.classList.toggle('select-active');
        },
        selectItem: function (event, item) {
            this.isCreated = false
            const defaultText = event.target.parentElement.previousElementSibling
            const input = defaultText.parentElement.querySelector('input')
            const menu = event.target.parentElement
            defaultText.innerHTML = item
            defaultText.value = item
            defaultText.style.color = '#444'
            input.value = item
            this.$emit('input', item)
            menu.classList.remove('select-active');
        },
    },
}
