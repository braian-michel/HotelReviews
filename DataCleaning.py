import pandas as pd
from geopy.geocoders import Nominatim

geolocalizador = Nominatim(user_agent="Mi_geolocalizador")

data = pd.read_csv(r"Hotel_Reviews.csv")

data['lat'] = data['lat'].astype(str)
data['lng'] = data['lng'].astype(str)
data['lat_lon'] = data['lat'] + ', ' + data['lng']

def replace_point(list_name, dataset, column):
    list_name = []
    dataset[column] = dataset[column].astype(str)

    for i in dataset[column]:
        i = i.replace('.',',')
        list_name.append(i)         

    dataset[column] = list_name


replace_point('latitud',data,'lat')
replace_point('longitud',data,'lng')
replace_point('score',data,'Average_Score')
replace_point ('rev_score', data, 'Reviewer_Score')



# Nuevo Dataframe con los datos de los reviewers y sus valoraciones
reviewers = data[['Hotel_Address', 'Hotel_Name','Average_Score','Review_Date','Reviewer_Nationality','Negative_Review', 
                  'Review_Total_Negative_Word_Counts','Positive_Review','Review_Total_Positive_Word_Counts',
                  'Total_Number_of_Reviews_Reviewer_Has_Given', 'Reviewer_Score', 'Tags','days_since_review']]



#Obtenemos sólo el número de días del contenido de la columan day_since_review
reviewers_ = reviewers.copy()

mask = []

for i in range(len(reviewers_)):
               row = reviewers_.loc[i,'days_since_review']
               row = row.split(maxsplit =2)[0]
               mask.append(row)

mask = list(map(int, mask))
reviewers_['days_since_review'] = mask

# Exportamos el dataset con los datos de los reviewers
reviewers_.to_csv('ReviewersData.csv')


#Nuevo Dataframe con los datos de localización de los hoteles
localiz = data[['Hotel_Address', 'Hotel_Name','Average_Score','Total_Number_of_Reviews','lat_lon','lat','lng']]
localiz = localiz.groupby(['Hotel_Address', 'Hotel_Name', 'Average_Score','lat_lon','lat','lng']).mean()

# Se pasa el Dataframe agrupado (localiz) a un csv y luego se lo importa (con el nombre htl_loc) para que las columnas agrupadas pasen a configurarse como columnas del Dataframe
localiz.to_csv('geoloc.csv')
htl_loc = pd.read_csv(r"geoloc.csv")

# Generamos columna "Hotel_City" a partir del geolocalizador
city_list = []

for i in htl_loc['lat_lon']:
    try:
        city = geolocalizador.reverse(i, language='en')
        city = city.raw['address']['city']
        city_list.append(city)
    except:
        city_list.append('Ciudad no encontrada')
htl_loc['Hotel_City'] = city_list


# Generamos columna "Hotel_Country" a partir del geolocalizador
country_list = []

for i in htl_loc['lat_lon']:
    try:
        country = geolocalizador.reverse(i, language='en')
        country = country.raw['address']['country']
        country_list.append(country)
    except:
        country_list.append('País no encontrado')
htl_loc['Hotel_Country'] = country_list


# Generamos un Dataframe con las columnas que nos interesan (en el orden deseado) para los datos de localización del hotel
htl_localiz = htl_loc[['Hotel_Address', 'Hotel_Name','Average_Score','Total_Number_of_Reviews','lat','lng','Hotel_City','Hotel_Country']]

# Completamos los valores faltantes de Hotel_City y Hotel_Country a partir d los datos de "Hotel_Address"
index_ = range(len(htl_localiz))
cities = list(htl_localiz['Hotel_City'].unique())
countries = list(htl_localiz['Hotel_Country'].unique())

for i in index_:
    for ci in cities:
        if htl_localiz['Hotel_City'][i] == 'Ciudad no encontrada' and htl_localiz['Hotel_Address'][i].find(ci)>=0:
            htl_localiz['Hotel_City'][i] = ci
            
print('Registros sin ciudad: ',len(htl_localiz[htl_localiz['Hotel_City'] == 'Ciudad no encontrada']))


for i in index_:
    for co in countries:
        if htl_localiz['Hotel_Country'][i] == 'País no encontrado' and htl_localiz['Hotel_Address'][i].find(co)>=0:
            htl_localiz['Hotel_Country'][i] = co
            
print('Registros sin país: ',len(htl_localiz[htl_localiz['Hotel_Country'] == 'País no encontrado']))


# Generamos un archivo csv con los datos de latitud y longitud, ciudad y país ajustados para su uso en Power BI.
htl_localiz.to_csv('HotelsData.csv')

