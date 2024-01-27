!pip install streamlit
!pip install streamlit_option_menu
!pip install easyocr
!pip install pandas
!pip install pillow
!pip install regex


%%writefile BizCardX.py
import streamlit as st
import pandas as pd
import easyocr
import streamlit  as st
from PIL import Image
import re
import sqlite3

#Streamlit part

st.set_page_config(page_title="BizcardX", page_icon="🚀",layout= "wide")


SELECT = option_menu(
    menu_title = None,
    options = ["Home", "Data Management","Contact"],
    icons =["🏡","🌍","🔚"],
    default_index=2,
    orientation="horizontal",
    styles={"container": {"padding": "0!important", "background-color": "white","size":"cover", "width": "100%"},
        "icon": {"color": "violet", "font-size": "20px"},
        "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#ff9933"},
        "nav-link-selected": {"background-color": "#ff9933"}})


# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://wallpapercave.com/wp/wp4478006.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True)
setting_bg()


if SELECT == "Home":
    col1,col2,col3 = st.columns(3)
    path = '/content/OCR3.png'
    photo = Image.open(path)
    col2.image(photo,width = 250)

    st.header(":rainbow[BizCardX: Extracting Business Card Data with OCR]")
    st.write()

    st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
    st.markdown("""## :green[**Overview :**] """Introducing BizCardX, a cutting-edge Streamlit application designed to seamlessly
                streamline the extraction of business card data through advanced Optical Character Recognition (OCR) technology.
                Users can effortlessly upload business card images, gaining instant access to vital details such as company names,
                cardholder information, and contact details. Emphasizing robust data security and user authentication, BizCardX
                ensures safe data storage while providing simplified management through its intuitive Streamlit User Interface.
                Immerse yourself in an efficient, secure, and user-friendly solution for effortlessly managing and organizing
                business card information with BizCardX.""")


#Main code
def extract_data(A):
  try:
    image = Image.open(A)
    read = easyocr.Reader(["en"], gpu = True)
    text = read.readtext(A, detail = False)
  except:
    st.warning("Invalid Image")
  return image, text


def images(text):

  data = {"Name" : [], 'Role' : [],'Websites': [], 'Gmail': [], 'Phone Number': [],"Company Name" : [], "Address" : [], 'Pincode': []}
  try:
    for texts in text:

      if "www " in texts or "www." in texts or "WWW" in texts or 'wWW' in texts or 'wwW' in texts or re.search(r"\b(?:www|global\.com)\b, re.IGNORECASE" ,texts):
        data['Websites'].append(texts)
      elif "@" in texts:
        data['Gmail'].append(texts)
      elif "+" in texts or "+91" in texts or re.search(r'\b(\d{3}-\d{3}-\d{4})\b', texts) or re.search(r'\+(\d{2})-(\d{3})-(\d{4})', texts):
        phone_number_match = re.search(r'\b(\d{3}-\d{3}-\d{4})\b', texts) or re.search(r'\+(\d{2})-(\d{3})-(\d{4})', texts)
        if phone_number_match:
            phone_number = phone_number_match.group(0)
            data['Phone Number'].append(phone_number)
      elif re.search(r'\b(\d{6}|\d{7})\b', texts):
        pin_code_match = re.search(r'\b(\d{6}|\d{7})\b', texts)
        if pin_code_match:
            pin_code = pin_code_match.group(1)
            data["Pincode"].append(pin_code)
      elif re.findall(r"^(\d+\s+\w+\s+\w+\s+(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)?)", texts):
         street_match = (r"^(\d+\s+\w+\s+\w+\s+(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)?)", texts)
         data["Address"].append(street_match[1])
      elif re.findall(r'(\d+\s+[A-Za-z\s,]+?)\s*,\s*([A-Za-z]+),\s*([A-Za-z]+);', texts):
        addresses = re.findall(r'(\d+\s+[A-Za-z\s,]+?)\s*,\s*([A-Za-z]+),\s*([A-Za-z]+);', texts)
        data["Address"].extend(addresses)
      elif re.findall(r'^\d+\s*[A-Za-z,]+$', texts):
        addresses = re.findall(r'^\d+\s*[A-Za-z,]+$', texts)
        data["Address"].extend(addresses)
      elif re.findall(r'^[A-Z]+$', texts ):
         addresses = re.findall(r'^[A-Z]+$', texts)
         data["Company Name"].extend(addresses)
      elif re.findall(r'\b[A-Z][a-z]*\b', texts) :
         addresses = re.findall(r'\b[A-Z][a-z]*\b', texts)
         data["Company Name"].extend(addresses)
      elif re.findall(r'^[a-z]+$', texts) :
         addresses = re.findall(r'^[a-z]+$', texts)
         data["Company Name"].extend(addresses)

    state_pattern = re.compile(r'\b([A-Za-z\s]+)\s+\d{6}\b')
    states = [state_pattern.search(s).group(1) for s in text if state_pattern.search(s)]
    data["Address"].append(states)

    state_pattern = re.compile(r'\b([A-Za-z\s]+)\s+\d{7}\b')
    states = [state_pattern.search(s).group(1) for s in text if state_pattern.search(s)]
    data["Address"].append(states)
    if text[0]:
      A = text[0]
      data["Name"].append(A)
    if text[1]:
      B = text[1]
      data["Role"].append(B)

  except:
        st.warning("Issue in Selecting the Text in Image")
  return data


def final(A):
  try:
    A['Company Name'] = A['Company Name'][-2:]
    A['Company Name'] = ' '.join(A['Company Name'])
    A["Address"] = [item for item in A['Address'] if item]

    if "Address" in A and len(A["Address"]) == 2:
      A['Address'][1] = A['Address'][1][0]
      A["Street"] =  A["Address"][0].split(",")[0].strip()
      A["City"] =  A["Address"][0].split(",")[1].strip()
      A["State"]  =   A["Address"][1]

    if ';' in A["Address"][0]:
      A["Address"][0] = A["Address"][0].replace(';', ',')

    A["Address"] = str(A['Address']).replace('(', '').replace(')', '')
    W = eval(A["Address"])
    A["Address"] = [item.strip() for item in W]

    if "Address" in A and len(A["Address"]) == 1:
      A["Street"] =  A["Address"][0].split(",")[0].strip()
      A["City"] =  A["Address"][0].split(",")[1].strip()
      A["State"]  = A["Address"][0].split(",")[2].strip()
    if len(A.get("Address", [])) >= 3:
      A["Street"] = A['Address'][0]
      A["City"] = A['Address'][1]
      A["State"] = A['Address'][2]

    A["Phone Number"] = [', '.join(A["Phone Number"])]
    A["Address"] = [', '.join(A["Address"])]
    for key, value in A.items():
      if not isinstance(value, list):
        A[key] = [value]

  except:
      st.warning("Issue in Pre-proccessing")

  return 'success'


if choice == 'EXPLORE':
    st.header(":orange[EXPLORE]")
    uploader = st.file_uploader("Upload Image To Fetch Text",type = ["png","jpg",'jpeg'])
    if uploader:
      with st.spinner("Please wait.."):
        image, text = extract_data(uploader.name)
        st.image(image)
        #st.success("Successfully Displayed Image")


def last(uploader):
   image, text = extract_data(uploader.name)
   data = images(text)
   final(data)
   return data

if choice == 'EXPLORE':
  if uploader:
    if st.button("Fetch Text"):
      with st.spinner("Please Wait..."):
        F = last(uploader)
        df = pd.DataFrame(F)
        st.write(df)
        st.success("Text Successfully Fetched!")


conn = sqlite3.connect('Bizdb')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS Cards(Name, Role, Websites,Gmail,Phone Number,Company Name,Address,Pincode,Street,City,State)")



if choice == "MODIFY":
  st.header(":blue[MODIFY]")
  uploaders = st.file_uploader("Upload Image To Fetch Text",type = ["png","jpg",'jpeg'])
  if uploaders:
      with st.spinner("Please Wait..."):
        F = last(uploaders)
        df = pd.DataFrame(F)
        st.write(df)
        st.success("Text Successfully Fetched!")
        if 'df':
            A = st.subheader("MODIFY")
            B = st.text_input("Name",df["Name"][0])
            C = st.text_input("Role",df['Role'][0])
            Z = st.text_input("Websites",df['Websites'][0])
            D = st.text_input("Gmail",df['Gmail'][0])
            E = st.text_input("Phone Number",df['Phone Number'][0])
            F = st.text_input("Company Name",df['Company Name'][0])
            G = st.text_input("Address",df['Address'][0])
            H = st.text_input("Street",df['Street'][0])
            I = st.text_input("City",df['City'][0])
            J = st.text_input("Pincode",df['Pincode'][0])
            K = st.text_input("State",df['State'][0])
            if st.button("Insert Into SQLITE3"):
              with st.spinner("Please Wait..."):
                query = """INSERT INTO Cards VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"""
                values = (B, C, Z, D, E, F, G, H, I, J, K)
                cur.execute(query, values)
                conn.commit()

            if st.button("VIEW"):
              with st.spinner("Please Wait..."):
                result = cur.execute("select * from Cards")
                X = result.fetchall()
                P = pd.DataFrame(X,columns = ["Name",'Role','Websites','Gmail','Phone Number' ,'Company Name','Address','Pincode','Street','City','State'])
                st.write(P)
                # st.button("CLEAR")




if choice == "EXPLORE MORE":
    st.header(":red[EXPLORE MORE]")
    uploaderss = st.file_uploader("Upload Image To Fetch Text",type = ["png","jpg",'jpeg'])
    if uploaderss:
      if st.button("FETCH"):
        with st.spinner("Wait.."):
          image, text = extract_data(uploaderss.name)
          st.image(image)
          st.success("Successfully Fetched Image")
          st.write(text)
          df = pd.DataFrame(text, columns = ["*TEXT DATA*"])
          st.write(df)
          st.success("Successfully Fetched Text From Image")
          st.button("Clear")


if choice=='DELETE':
  st.header(":orange[DELETE]")
  M = st.selectbox("Select Name",['Select Name','Selva',"KARTHICK",'REVANTH','SANTHOSH'])
  if M!="Select Name":
    if st.button('Delete From SQLITE3'):
      with st.spinner("Please Wait.."):
        delete_query = "DELETE FROM Cards WHERE Name = ?"
        cur.execute(delete_query, (M,))
        conn.commit()
  if st.button("VIEW"):
          with st.spinner("Please Wait..."):
            result = cur.execute("select * from Cards")
            X = result.fetchall()
            P = pd.DataFrame(X,columns = ["Name",'Role','Websites','Gmail','Phone Number' ,'Company Name','Address','Pincode','Street','City','State'])
            st.write(P)
            st.button("CLEAR")

!npm install localtunnel

!streamlit run /content/BizcardX.py &>/content/logs.txt & npx localtunnel --port 8501 & curl ipv4.icanhazip.com
