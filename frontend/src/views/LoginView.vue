<template>
    <div class="mt-5">
        <h1>login de Usuario</h1>
        <div class="m-auto text-left" style="max-width: 400px">   
            <Login @logou="logou" rota="/user/token/"></Login>
        </div>
    </div>
</template>

<script>
import Login from '@/components/LoginComp.vue'
export default {
    components:{
        Login
    },methods:{
        logou(){
            setTimeout(() => {
                this.$router.push('/');
            }, 2000);
            
        }
    }
}
</script>