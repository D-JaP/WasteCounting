Chart.register(ChartDataLabels);


let globalChart

const input = document.querySelector('input');
    const preview = document.querySelector('.preview');

    input.style.opacity = 0;

    input.addEventListener('change', updateImageDisplay);

    function updateImageDisplay() {
      while(preview.firstChild) {
        preview.removeChild(preview.firstChild);
      }

      const curFiles = input.files;
      if(curFiles.length === 0) {
        const para = document.createElement('p');
        para.textContent = 'No files currently selected for upload';
        preview.appendChild(para);
      } else {
        const list = document.createElement('ol');
        preview.appendChild(list);

        for(const file of curFiles) {
          const listItem = document.createElement('li');
          const para = document.createElement('p');

          if(validFileType(file)) {
            para.textContent = `File name ${file.name}, file size ${returnFileSize(file.size)}.`;
            const image = document.createElement('img');
            image.src = URL.createObjectURL(file);

            listItem.appendChild(image);
            listItem.appendChild(para);
          } else {
            para.textContent = `File name ${file.name}: Not a valid file type. Update your selection.`;
            listItem.appendChild(para);
          }

          list.appendChild(listItem);
        }
      }
    }

// https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types
    const fileTypes = [
        'image/bmp',
        'image/gif',
        'image/jpeg',
        'image/pjpeg',
        'image/png',
        'image/tiff',
        'image/webp',
        `image/x-icon`
    ];

    function validFileType(file) {
      return fileTypes.includes(file.type);
    }

    function returnFileSize(number) {
      if(number < 1024) {
        return number + 'bytes';
      } else if(number > 1024 && number < 1048576) {
        return (number/1024).toFixed(1) + 'KB';
      } else if(number > 1048576) {
        return (number/1048576).toFixed(1) + 'MB';
      }
    }


// submit button

function submitForm(event){
  event.preventDefault();
  
  var formdata = new FormData(document.getElementById('form_submit'))
  // enterLoading State
  const activeLoading = () => {
    const loadingIcon = document.querySelector(".spinner")
    loadingIcon.style.display = "block"
  }
  const deactiveLoading = () => {
    const loadingIcon = document.querySelector(".spinner")
    loadingIcon.style.display = "none"
  }
  activeLoading()

  try {
    globalChart.destroy()
  }
  catch{
    
  }
  fetch("/submit", {
    method: 'POST',
    body: formdata
  })
  .then(response => response.json())
    .then(data => {
        // Handle the response (optional)
        console.log(data);
        // Show the form after successful submission
        createChart(data)
        addBreakdownImage(data)
        deactiveLoading()
    })
    .catch(error => {
        // Handle errors (optional)
        deactiveLoading()
        console.error(error);
    });
  
}


function createChart(json_response){
  var firstItem = json_response["data"][0]
  var keys = Object.keys(firstItem[Object.keys(firstItem)[0]]);
  var sum = {}
  keys.forEach(key => {
    sum[key] = 0
  })

  for (let img of json_response["data"]){
    var curr_key = Object.keys(img)
    keys.forEach(key=>{
      sum[key] += img[curr_key][key]["count"]
    })
  }


  var xValues = keys
  var yValues = keys.map(key => sum[key])

  
  
  var barColors = [
    'rgba(255, 99, 132, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(255, 205, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(54, 162, 235, 0.8)']

  var borderColor= [
    'rgb(255, 99, 132)',
    'rgb(255, 159, 64)',
    'rgb(255, 205, 86)',
    'rgb(75, 192, 192)',
    'rgb(54, 162, 235)']
  const mychart = document.querySelector("#myChart")
  mychart.style.display = "block"
  globalChart = new Chart("myChart", {
    type: "bar",
    data: {
      labels: xValues,
      datasets: [{
        label : "summary",
        backgroundColor: barColors,
        borderColor: borderColor,
        borderWidth :1,
        data: yValues,
        datalabels: {
          align: 'center',
          anchor: 'end'
        }
  
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        datalabels: {
          color: 'black',
          font: {
            weight: 'bold'
          },
          formatter: Math.round
        }
      },

    }
  });
}

const img_tab  = (img_name, img_data) => {
  const imagenclass = (class_name, count , img_path) => `<h4 style="text-align: center;">${class_name} : <span>${count}</span></h4>
                        <img src="${img_path}" type ="jpg" alt="" style="width: 960px;margin-left:auto;margin-right:auto" >`
  const keys = Object.keys(img_data)

  return `<div class="image-bar d-flex-center" style="margin-left: auto; margin-right: auto;margin-bottom: 20px;transition: display 0.5s"  onclick="expandImage(event)">
            <h3 style="padding: 20px; margin: 0;" class="img-name" >${img_name} </h3>
            <div class="pad20 d-flex-center expanding" style="display: none;" >
                ${
                  keys.flatMap(key => {return imagenclass(key,img_data[key]["count"], img_data[key]["path"])}).join('')
                }
            </div>
          </div>`
}

function addBreakdownImage(json_response){
  const imgContainer = document.querySelector("#img_summary")
  for (let img of json_response["data"]){
    var curr_key = Object.keys(img)
    // Create a new DOMParser
    const parser = new DOMParser();

    // Parse the HTML string
    const parsedHtml = parser.parseFromString(img_tab(curr_key, img[curr_key]), 'text/html');

    // Get the root node (body) of the parsed HTML
    const rootNode = parsedHtml.body;
    imgContainer.appendChild(rootNode)
  }
}

function expandImage(event){
  const curr_element = event.target.parentNode
  const expandableElement = curr_element.querySelector(".expanding")
  if (expandableElement.style.display === 'none' || expandableElement.style.display === '') {
    expandableElement.style.display = 'block';
  } else {
    expandableElement.style.display = 'none';
  }
}