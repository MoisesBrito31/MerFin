<template>
  <div>
    <b-overlay :show="sucesso" rounded="sm">
      <template #overlay>
        <div class="text-center">
          <b-icon variant="success" icon="check2-circle" font-scale="3" animation="fade"></b-icon>
        </div>
      </template>
    <div class="card-header mb-3 mt-5">
      <img class="mr-3" src="../assets/logo.jpeg" width="300px">
    </div>
            
            
    <b-form-group label="Usuário:" :state="userOK"  invalid-feedback="Não pode ser Vazio">
      <b-form-input :state="userOK" 
          type="text" v-model="username" trim >
      </b-form-input>
    </b-form-group>
       
    <b-form-group label="Senha:" :state="senhaOK"  invalid-feedback="Não pode ser Vazio">
       <b-form-input :state="senhaOK" 
          type="password" v-model="password" trim >
      </b-form-input>
    </b-form-group>
        
        <b-form-group class="mt-3 pt-3" >
            <b-button @click="login" v-bind:class="{disabled:!podeCadastrar}"  block variant="primary">
                <span v-show="espera">
                <b-spinner type="grow" variant="light"></b-spinner>
                <b-spinner type="grow" variant="light"></b-spinner>
                <b-spinner type="grow" variant="light"></b-spinner>
               </span>
               <span v-show="!espera">Entrar</span>
            </b-button>
        </b-form-group>
      </b-overlay>
        <div>
          <!--Alerta de falha-->
          <b-alert
            :show="alertaFalha.time"
            dismissible
            variant="danger"
            @dismissed="alertaFalha.time=0"
            @dismiss-count-down="alertaFalhaTick"
          >
            <p>{{ alertaFalha.msg }}</p>
            <b-progress
              variant="danger"
              :max="alertaFalha.startTime"
              :value="alertaFalha.time"
              height="4px"
            ></b-progress>
          </b-alert>
        </div>
    </div>
  </template>
  
  <script>
  import { mapMutations } from 'vuex';
  import { mapGetters } from 'vuex';
  import Cookies from 'js-cookie'
  export default {
    data() {
      return {
        alertaFalha:{
          'startTime':10,
          'time':0,
          'msg':''
        },
        sucesso:false,
        username: '',
        password: '',
        espera: false,
      };
    },
    computed:{
      ...mapGetters(['getDominio']),
      senhaOK(){
        if (this.password.length>0){return true}
        else{return false}
      },
      userOK(){
        if (this.username.length>0){return true}
        else{return false}
      },
      podeCadastrar(){
        if (this.userOK && this.senhaOK){ return true}
        else{ return false}
      },
    },
    methods: {
      ...mapMutations(['logar']),
      alertaFalhaTick(valor){
        this.alertaFalha.time = valor
      },
      async login() {
        try {
          this.espera = true
          const response = await fetch(`${this.getDominio}${this.rota}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: this.username,
              password: this.password
            })
          });
  
          if (response.ok) {
            const data = await response.json();
            this.espera=false
            this.sucesso=true
            this.logar(data.token);
            Cookies.set('token',data.token);
            this.$emit('logou')
          } else {
            if(response.status==400){
              throw new Error('User ou senha Incorretos');
            }else{
              throw new Error('Erro interno no servidor');
            }
          }
        } catch (error) {
          this.espera=false
          this.alertaFalha.msg= error
          this.alertaFalha.time= this.alertaFalha.startTime
          console.error(error);
        }
      },
    },
    props:{
      rota:{'type':String}
    }
  };
  </script>
  