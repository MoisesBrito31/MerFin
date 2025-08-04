<template>
    <div>
        <b-modal size="lg" v-model="modalEstado" ok-only @hide="getDadosEstado">
            <!--estado add aqui-->
            <EstadoDataAdd></EstadoDataAdd>
        </b-modal>
        <div class="card-header mb-3">
            <h4> Cadastro de OS</h4>
        </div>
        <b-form>
            <b-form-group label="Cliente:" :state="clienteOK"  invalid-feedback="Não pode ser Vazio">
            <b-input-group>
                <b-form-input :state="clienteOK" 
                    type="text" placeholder="Fabricante" v-model="obj.name" trim >
                </b-form-input>
            </b-input-group>
        </b-form-group>
        <b-form-group label="Serviço:" :state="serviceOK"  invalid-feedback="Não pode ser Vazio">
            <b-input-group>
                <b-form-input :state="serviceOK" 
                    type="text" placeholder="Serviço" v-model="obj.description" trim >
                </b-form-input>
            </b-input-group>
        </b-form-group>
        <b-form-group label="Estado:" :state=estadoOK class="mr-5">
            <b-input-group>
                <b-form-select class="mr-2" :state=estadoOK v-model="obj.estado" :options="estado" ></b-form-select>
                <b-button @click="modalEstado=true" variant='primary'>
                    <b-icon icon='plus'></b-icon>
                </b-button>
            </b-input-group>           
        </b-form-group>
        
        <b-form-group class="mt-3 pt-3" >
            <b-button @click="postDadosOS" v-bind:class="{disabled:!podeCadastrar}"  block variant="primary">
                <span v-show="espera">
                <b-spinner type="grow" variant="light"></b-spinner>
                <b-spinner type="grow" variant="light"></b-spinner>
                <b-spinner type="grow" variant="light"></b-spinner>
               </span>
               <span v-show="!espera">Cadastrar</span>
            </b-button>
        </b-form-group>
        </b-form>
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
import EstadoDataAdd from '@/components/estado/data-Add.vue'
export default {
  name: 'data-Add',
  components:{
    EstadoDataAdd,
  },
  data(){
    return{
        alertaFalha:{
          'startTime':10,
          'time':0,
          'msg':''
        },
        modalVisible:false,
        modalEstado:false,
        erroMsg : '',
        espera:false,
        falha: false,
        obj:{'name':'','description':'','estado':0},
        estado:[],
        objEstado:[],

    }
  },
  created(){
    this.getDadosEstado()
  },
  computed:{
    ...mapGetters(['getDominio','getToken']),
    clienteOK(){
        if(this.obj.name.length>0){return true}
        else{return false}
    },
    serviceOK(){
        if(this.obj.description.length>0){return true}
        else{return false}
    },
    estadoOK(){
        try{
        if(this.obj.estado>0){return true}
        else{return false}
        }catch{
          return false
        }
    },
    podeCadastrar(){
        if (this.clienteOK && this.serviceOK && this.estadoOK){ return true}
        else{ return false}
    }
  },methods:{
    alertaFalhaTick(valor){
      this.alertaFalha.time = valor
    },
    mostarMsgOK(){
      this.$bvToast.toast('Criado!!!', {
            title: "Bem Sucedido",
            variant: "success",
            solid: true
          })
      this.obj = {'name':'','description':''}
    },
    dataFormat(){
      const formdata = new FormData()
      formdata.append('name',this.obj.name)
      formdata.append('description',this.obj.description)
      formdata.append('state',this.obj.estado)
      //var estado = {}
      //this.objEstado.forEach(x => {
      //       if(x.id == this.obj.estado){
      //         estado = x
      //       }})
      return formdata
      //return JSON.stringify(valor)
           ////const form = document.getElementById('img')
           ////const file = form.files[0]
           //const formdata = new FormData()
           ////if(file!==undefined){formdata.append('img',file,file.name)}
           ////if(this.obj.id!==undefined){formdata.append('id',this.obj.id)}
           //formdata.append('name',this.obj.name)
           //formdata.append('description',this.obj.description)
           ////formdata.append('state',this.obj.estado)
           //this.objEstado.forEach(x => {
           //  if(x.id == this.obj.estado){
           //    formdata.append('state',JSON.stringify(x))
           //    //formdata.append('state',x)
           //  }
           //});
           //return formdata
    },
    async postDadosOS(){
        this.espera=true
        try{
        this.esperando = true
          const response = await fetch(`${this.getDominio}/api/os/`,{
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
    async getDadosEstado(){
      try{
        this.esperandoDados = true
          const response = await fetch(`${this.getDominio}/api/os/estado/`,{
          headers:{
            'Authorization': `Token ${this.getToken}`
          }
        })
        if(response.ok){
          const data = await response.json()
          this.esperandoDados = false
          this.objEstado = data
          this.estado = []
          for(var x=0 ; x< data.length; x++){
                    this.estado.push({'value':data[x].id,'text':data[x].name})
          }
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

  }

}
</script>