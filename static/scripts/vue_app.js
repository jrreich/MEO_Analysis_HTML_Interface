

Vue.prototype.$http = axios

var app = new Vue({
    el: '#app',
    data: {
        message:"yeah buddy"
    },
    delimiters: ["[[","]]"]
});

var app2 = new Vue({
  el: '#app2',
  data: {
    message: "nonono"
  },
  delimiters: ["[[","]]"]
})

new Vue({
  el: '#app3',
  data () {
    return {
      info: null
    }
  },
  mounted () {
    axios
      .get('http://localhost:8081/api/comp/162503')
      .then(response => (this.info = response))
  },
  delimiters: ["[[","]]"]
})

