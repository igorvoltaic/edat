export default {
    name: 'dropdown-select',
    template: '#dropdown-select-template',
    delimiters: ['[[',']]'],
    props: ['items', 'name' ],
    data() {
        return {
            isActive: false
        }
    },
    methods: {
        classToggle: function(event) {
            const menu = event.target.parentElement.querySelector('.dropdown-menu')
            menu.classList.toggle('select-active');
        },
        selectItem: function (event, item) {
            const defaultText = event.target.parentElement.previousElementSibling
            const input = defaultText.parentElement.querySelector('input')
            const menu = event.target.parentElement
            defaultText.innerHTML = item
            defaultText.value = item
            defaultText.style.color = '#444'
            const old = input.value
            input.value = item
            this.$emit('input', item)
            menu.classList.remove('select-active');
        },
    },
}
