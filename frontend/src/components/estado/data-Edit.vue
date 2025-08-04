<template>
    <div>
        <b-overlay rounded="sm" :show="esperandoDados">
            <div class="card-header mb-3">
                <h4> Edição de {{ obj.name }}</h4>
            </div>
            <b-form>
                <b-form-group label="Estado:" :state="EstadoOK"  invalid-feedback="Não pode ser Vazio">
                <b-input-group>
                    <b-form-input :state="EstadoOK" 
                        type="text" placeholder="descrição" v-model="obj.name" trim >
                    </b-form-input>
                </b-input-group>
            </b-form-group>
            <b-form-group label="Cor:">
                <b-input-group>
                    <b-form-input 
                        type="color" v-model="obj.color">
                    </b-form-input>
                </b-input-group>
            </b-form-group>
            
            <b-form-group class="mt-3 pt-3" >
                <b-button @click="postDadosOS" v-bind:class="{disabled:!podeCadastrar}"  block variant="primary">
                    <span v-show="espera">
                    <b-spinner type="grow" variant="light"></b-spinner>
                    <b-spinner type="grow" variant="light"></b-spinner>
                    <b-spinner type="grow" variant="light"></b-spinner>
                </span>
                <span v-show="!espera">Salvar</span>
                </b-button>
            </b-form-group>
            </b-form>
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

<script lang="js">
import { mapGetters } from 'vuex'
export default {
  name: 'data-Add',
  created(){
    this.getDadosOS()
  },
  data(){
    return{
        alertaFalha:{
          'startTime':10,
          'time':0,
          'msg':''
        },
        modalVisible:false,
        erroMsg : '',
        espera:false,
        esperandoDados:false,
        falha: false,
        obj:{'name':'','color':''}
    }
  },computed:{
    ...mapGetters(['getDominio','getToken']),
    EstadoOK(){
        if(this.obj.name.length>0){return true}
        else{return false}
    },
    podeCadastrar(){
        if (this.EstadoOK ){ return true}
        else{ return false}
    }
  },methods:{
    alertaFalhaTick(valor){
      this.alertaFalha.time = valor
    },
    mostarMsgOK(){
        this.$emit("editado")
    },
    dataFormat(){
            //const form = document.getElementById('img')
            //const file = form.files[0]
            const formdata = new FormData()
            //if(file!==undefined){formdata.append('img',file,file.name)}
            //if(this.obj.id!==undefined){formdata.append('id',this.obj.id)}
            formdata.append('name',this.obj.name)
            formdata.append('color',this.obj.color)
            formdata.append('colorHTML',`color:${this.obj.color};`)
            return formdata
    },
    async postDadosOS(){
        this.espera=true
        try{
        this.esperando = true
          const response = await fetch(`${this.getDominio}/api/os/estado/${this.id}/`,{
            method:"POST",
            headers:{
            'Authorization': `Token ${this.getToken}`
          },body:this.dataFormat()
        })
        if(response.ok){
          this.mostarMsgOK()
          this.espera = false
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
        this.alertaFalha.msg= error
        this.alertaFalha.time= this.alertaFalha.startTime
        this.espera = false
      }
       
    },
    async getDadosOS(){
      try{
        this.esperandoDados = true
          const response = await fetch(`${this.getDominio}/api/os/estado/${this.id}/`,{
          headers:{
            'Authorization': `Token ${this.getToken}`
          }
        })
        if(response.ok){
          const data = await response.json()
          this.esperandoDados = false
          this.obj = data
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
        this.alertaFalha.msg= error
        this.alertaFalha.time= this.alertaFalha.startTime
        this.esperandoDados = false
      }
    },

  },props:{
    id:{type: Number,  required:false,}
  }

}
</script>