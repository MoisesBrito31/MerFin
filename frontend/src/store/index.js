import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
      dominio: 'http://localhost:8000',
      logado: false,
      nome: 'Desconhecido',
      usuarioAlertas:0,
      token: '',
      avatar: '',
  },
  getters: {	  
    logado(state){
      return state.logado
    },
    getName(state){return state.nome},
    getAlertas(state){return state.usuarioAlertas},
    getAvatar(state){return state.avatar},
    getToken(state){return state.token},
    getDominio(state){return state.dominio}
  },
  mutations: {	
    logar(state,token){
      state.logado = true
      state.token = token
    },
    logout(state){
      state.logado = false
      state.token = ''
    },
    setUser(state,name){state.nome = name},
    setAvatar(state,avatar){state.avatar=avatar},
    setAlertas(state,alerta){state.usuarioAlertas=alerta}
  },
  actions: {
  },
  modules: {
  }
})
