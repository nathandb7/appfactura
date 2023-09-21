import './style.css'
import javascriptLogo from './javascript.svg'

async function test_api(){
    let response = await fetch("/api/hello-world");
    let data = await response.json();
    return data;
};

async function main(){
    console.log("calling api...");
    let data = await test_api();
    let h = document.querySelector('.api-test');
    h.innerHTML = "Api sends: " + JSON.stringify(data);
};

document.addEventListener("DOMContentLoaded", main);

document.querySelector('#app').innerHTML = `
  <div>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank">
      <img src="${javascriptLogo}" class="logo vanilla" alt="JavaScript logo" />
    </a>
    <h2 class="api-test"></h2>
  </div>
`
