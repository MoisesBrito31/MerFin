<template> 
    <div>
        <b-navbar toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand href="/">
      <img class="mr-3" src="../assets/logo.jpeg" width="120" height="40">
    </b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-button variant="info" @click="gourl('')" >Home</b-button>
        <b-button variant="info" @click="gourl('page1')" >Pagina 1</b-button>
        <b-button variant="info" @click="gourl('page2')" >Pagina 2</b-button>
        <b-button variant="info" @click="gourl('login')" >Logar</b-button>
      </b-navbar-nav>

      <b-navbar-nav class="ml-auto mr-2" v-if="logado">
        <b-nav-item-dropdown right>
          <template #button-content>
            <em>
              Olá {{getName}}
              <b-avatar v-if="getAlertas>0" :badge="getAlertas" badge-variant="warning" :src="avatar"></b-avatar>
              <b-avatar v-else :src="avatar"></b-avatar>
            </em>
          </template>
          <div>
             <b-button @click="logout" variant="primary">sair</b-button>
          </div>
        </b-nav-item-dropdown>
      </b-navbar-nav>

    </b-collapse>
  </b-navbar>
       
    </div>
</template> 

<script lang="js">
  import { mapGetters } from 'vuex'; 
  import { mapMutations } from 'vuex'; 
  import Cookies from 'js-cookie' 
  export default {
    name: 'mainMenu',
    created(){
      this.getUserData()
      setInterval(() => {
        this.getUserData()
      },10000);
    },
    computed:{...mapGetters(['logado','getName','getAlertas','getDominio','getAvatar','getToken']),
      avatar(){
        return `${this.getDominio}${this.getAvatar}`
      }
    },
    methods:{
        ...mapMutations(['setUser','setAvatar','setAlertas']),
        gourl(url){
            this.$router.push(`/${url}`);
        },
        async logout(){
            Cookies.remove('token')
            this.gourl('')
        },
        async getUserData(){
      try{
        this.esperando = true
          const response = await fetch(`${this.getDominio}/user/getuserdata/`,{
          headers:{
            'Authorization': `Token ${this.getToken}`
          }
        })
        if(response.ok){
          const data = await response.json()
          this.setUser(data.name)
          this.setAlertas(data.alertas)
          this.setAvatar(data.avatar)
        }else{
          switch(response.status){
            case 401:
              throw new Error('Não Autorizado');
            case 404:
              throw new Error('Não Encontrado');
            default:
              throw new Error('Falha interna no Servidor');
          }
        }
      }catch(error){     
        console.log(error)
      }
    },
    }
  }
</script>