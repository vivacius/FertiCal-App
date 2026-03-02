################Recomendaciones masivas de fertilizacion########################
# -------------------------------------------------------------------------
# Libraries----------------------------------------------------------------
# -------------------------------------------------------------------------
require(pacman)
pacman::p_load(raster, rgdal, rgeos, stringr, sf, tidyverse, RColorBrewer, cowplot, ggpubr, shiny,dplyr,tibble,
               ggspatial, rnaturalearth, rnaturalearthdata,readxl,png,ggplot2,animation,geodata,gtools,RSAGA,fs,cptcity,
               jsonlite,DT,kableExtra,tables,Hmisc,knitr,kableExtra,webshot,magrittr,readxl,foreign,lubridate,geoR,sp,
               shinyWidgets,shinydashboard,dashboardthemes,gstat,spatstat, openxlsx)

# -------------------------------------------------------------------------
# Globals variables--------------------------------------------------------
# -------------------------------------------------------------------------
Efi <- read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Tabla_eficiencia.csv", sep = ";")
Efi_variedades <- read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Eficiencia_variedades.csv", sep = ";")
tab<-readOGR("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Fertilizacion shp/Suertes_Total_Fertilizacion.shp")#----------------------------------FALTA PERMISO PNSIG01>>>SE USA LOCAL
#CRS("+proj=tmerc +lat_0=4.59904722222222 +lon_0=-77.0809166666667 +k=1 +x_0=1000000 +y_0=1000000 +ellps=intl +towgs84=307,304,-318,0,0,0,0 +units=m +no_defs")

df_recomendacion <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Recomendacion.xlsx", 
                               col_types = c("text", "text", "text", 
                                             "numeric", "numeric", "text", "text", 
                                             "text", "text", "text", "text", "numeric", 
                                             "numeric"))
df_unid_correg <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Recomendacion.xlsx", 
                             sheet = "Unidades_corregidas")
semana_r <- "Semana 50"#-------------------------------------------------------------------------------------------------------------------------IMPORTANTE CAMBIAR SEMANA

ruth_download <- paste0("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Salidas/",df_recomendacion$Zona[1])
########Creacion de carpetas estructura de datos##############
dir.create(ruth_download)
dir.create(paste0(ruth_download, "/" ,as.character(year(Sys.Date()))))
dir.create(paste0(ruth_download, "/" ,as.character(year(Sys.Date())), "/", semana_r))
dir.create(paste0(ruth_download, "/" ,as.character(year(Sys.Date())), "/", semana_r, "/", semana_r, "_excel"))
########Rutas de carpeta donde almacenar##############
ruth_s <- paste0(ruth_download, "/" ,as.character(year(Sys.Date())), "/", semana_r)
ruth_e <- paste0(ruth_download, "/" ,as.character(year(Sys.Date())), "/", semana_r, "/", semana_r, "_excel")
# -------------------------------------------------------------------------
# recomend Functions-------------------------------------------------------
# -------------------------------------------------------------------------


recomendation <- function(hda, ste, Naxtrom = 0, Nitro_Xtends = 0, SAM = 0, Nitrax = 0, Urea = 0, fert = NULL, shape, Efi, area, areaR) {
  
  datosArea <- function(Hda,ste) {
    
    library(RODBC)
    
    my_server = "AGROIPSAVDB01\\PROD"
    my_db = "SIAGRI_AG"
    my_username = "sg_interf"
    my_pwd = "PIFAC4598"
    
    conexionSIAGRI <- odbcDriverConnect(paste0("DRIVER={SQL Server Native Client 11.0};
                                               server=", my_server, "; 
                                               database=", my_db, "; 
                                               uid=", my_username, "; 
                                               pwd=", my_pwd))
    
    #Seleccion de datos de entrenamiento
    QuerySql <- paste0("SELECT AREA_P AREA FROM TALHAO WITH(NOLOCK) WHERE FAZ = '", Hda, "' AND TAL = '", ste,"'", sep="")
    
    data <- sqlQuery(conexionSIAGRI, QuerySql)
    
    
    odbcClose(conexionSIAGRI)
    
    return(data)
    
  }
  data<-datosArea(hda,ste)
  data[1,1] <- areaR
  
  proporcion<-data.frame()
  proporcion[1,1]<-(Naxtrom)/100
  proporcion[1,2]<-(Nitro_Xtends)/100
  proporcion[1,3]<-(SAM)/100
  proporcion[1,4]<-(Nitrax)/100
  proporcion[1,5]<-(Urea)/100
  names(proporcion)<-c("Naxtrom","Nitro_Xtends","SAM","Nitrax","Urea")
  shp <- shape
  ph_prom<-round(mean(shp$ph),2)
  #ph_prom<-ph
  fert<-fert
  
  tabla_recomendacion<-data.frame()
  
  if(sum(proporcion[1,])==0){
    if(ph_prom<=7.2){
      a<-which(Efi$Fertilizante==fert[1])
      tabla_recomendacion[1,1]<-round(mean(shp$Dosis)/as.numeric(Efi$Eficiencia.de.absorcion[a]),2)
      if (tabla_recomendacion[1,1]<138){
        b<-0
        tabla_recomendacion[1,1]<-138
      }else{
        if(tabla_recomendacion[1,1]>186){
          b<-tabla_recomendacion[1,1]-186
          tabla_recomendacion[1,1]<-186
        }else{
          tabla_recomendacion[1,1]<-tabla_recomendacion[1,1]
          b<-0
        }
      }
      tabla_recomendacion[1,2]<-round(tabla_recomendacion[1,1]/as.numeric(Efi$Porcentaje.de.concentracion[a]),2)
      tabla_recomendacion[1,3]<-round(tabla_recomendacion[1,2]*data[1,1],2)
      tabla_recomendacion[1,4]<-round(tabla_recomendacion[1,3]/50,2)
      tabla_recomendacion[1,5]<-round(tabla_recomendacion[1,3]*as.numeric(Efi$Costo.Kg[a]),2)
      tabla_recomendacion[1,6]<-b
      names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo")
      row.names(tabla_recomendacion)<-fert[1]
    }else{
      if(ph_prom>7.2 & ph_prom<=7.6){
        a<-which(Efi$Fertilizante==fert[1])
        tabla_recomendacion[1,1]<-round(mean(shp$Dosis)/as.numeric(Efi$Eficiencia.de.absorcion[a]),2)
        if (tabla_recomendacion[1,1]<138){
          b<-0
          tabla_recomendacion[1,1]<-138
        }else{
          if(tabla_recomendacion[1,1]>186){
            b<-tabla_recomendacion[1,1]-186
            tabla_recomendacion[1,1]<-186
          }else{
            tabla_recomendacion[1,1]<-tabla_recomendacion[1,1]
            b<-0
          }
        }
        tabla_recomendacion[1,2]<-round(tabla_recomendacion[1,1]/as.numeric(Efi$Porcentaje.de.concentracion[a]),2)
        tabla_recomendacion[1,3]<-round(tabla_recomendacion[1,2]*data[1,1],2)
        tabla_recomendacion[1,4]<-round(tabla_recomendacion[1,3]/50,2)
        tabla_recomendacion[1,5]<-round(tabla_recomendacion[1,3]*as.numeric(Efi$Costo.Kg[a]),2)
        tabla_recomendacion[1,6]<-b
        names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo")
        row.names(tabla_recomendacion)<-fert[1]
      }else{
        if(ph_prom>7.6 && ph_prom<=8.3){
          dosis<-(((mean(shp$Dosis) * 0.5) / (Efi$Eficiencia.de.absorcion[which(Efi$Fertilizante==fert[1])])) + ((mean(shp$Dosis) * 0.5) / (Efi$Eficiencia.de.absorcion[which(Efi$Fertilizante==fert[2])])))
          if (dosis < 138){
            dosis <- 138
            b <- 0
          }else{
            if (dosis > 186){
              b <- dosis - 186
              dosis <- 186
            }else{
              dosis <- dosis
              b <- 0
            }
          }
          
          for (i in 1:length(fert)) {
            tabla_recomendacion[i,1]<-round(dosis*0.5,2)
            tabla_recomendacion[i,2]<-round((dosis*0.5)/Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fert[i])],2)
            tabla_recomendacion[i,3]<-round(tabla_recomendacion[i,2]*data[1,1],2)
            tabla_recomendacion[i,4]<-round(tabla_recomendacion[i,3]/50,2)
            tabla_recomendacion[i,5]<-round(tabla_recomendacion[i,2]*Efi$Costo.Kg[which(Efi$Fertilizante==fert[i])],2)
            tabla_recomendacion[i,6]<-b
          }
          names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo")
          row.names(tabla_recomendacion)<-fert
        }else{
          dosis<-(((mean(shp$Dosis) * 0.6) / (Efi$Eficiencia.de.absorcion[which(Efi$Fertilizante==fert[1])])) + ((mean(shp$Dosis) * 0.4) / (Efi$Eficiencia.de.absorcion[which(Efi$Fertilizante==fert[2])])))
          if (dosis < 138){
            dosis <- 138
            b <- 0
          }else{
            if (dosis > 186){
              b <- dosis - 186
              dosis <- 186
            }else{
              dosis <- dosis
              b <- 0
            }
          }
          
          porcentaje_vec <- c(0.6, 0.4)
          for (i in 1:length(fert)) {
            tabla_recomendacion[i,1]<-round(dosis*porcentaje_vec[i],2)
            tabla_recomendacion[i,2]<-round((dosis*porcentaje_vec[i])/Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fert[i])],2)
            tabla_recomendacion[i,3]<-round(tabla_recomendacion[i,2]*data[1,1],2)
            tabla_recomendacion[i,4]<-round(tabla_recomendacion[i,3]/50,2)
            tabla_recomendacion[i,5]<-round(tabla_recomendacion[i,2]*Efi$Costo.Kg[which(Efi$Fertilizante==fert[i])],2)
            tabla_recomendacion[i,6]<-b
          }
          names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo")
          row.names(tabla_recomendacion)<-fert
        }
      }
    }
  }else{
    a<-0
    for (i in fert) {
      a<-a+((proporcion[1,which(names(proporcion)==i)])/Efi$Eficiencia.de.absorcion[which(Efi$Fertilizante==i)])
    }
    dosis<-mean(shp$Dosis) * as.numeric(a)
    if (dosis < 138){
      dosis <- 138
      b <- 0
    }else{
      if (dosis > 186){
        b <- dosis - 186
        dosis <- 186
      }else{
        dosis <- dosis
        b <- 0
      }
    }
    
    cont1<-1
    for (i in fert) {
      prop1<-(proporcion[1,which(names(proporcion)==i)]) 
      tabla_recomendacion[cont1,1]<-round(dosis*prop1,2)
      tabla_recomendacion[cont1,2]<-round((dosis*proporcion[1,which(names(proporcion)==i)])/Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==i)],2)
      tabla_recomendacion[cont1,3]<-round(tabla_recomendacion[cont1,2]*data[1,1],2)
      tabla_recomendacion[cont1,4]<-round(tabla_recomendacion[cont1,3]/50,2)
      tabla_recomendacion[cont1,5]<-round(tabla_recomendacion[cont1,2]*Efi$Costo.Kg[which(Efi$Fertilizante==fert[cont1])],2)
      tabla_recomendacion[cont1,6]<-b
      cont1<-cont1+1
    }
    names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo")
    row.names(tabla_recomendacion)<-fert
  }
  return(as.data.frame(tabla_recomendacion)) 
  
}

recomendation_f <- function(hda, ste, proporcion, fert = NULL, fert1 = NULL, shape, Efi, area, areaR, prop_fracc) {
  
  datosArea <- function(Hda,ste) {
    
    library(RODBC)
    
    my_server = "AGROIPSAVDB01\\PROD"
    my_db = "SIAGRI_AG"
    my_username = "sg_interf"
    my_pwd = "PIFAC4598"
    
    conexionSIAGRI <- odbcDriverConnect(paste0("DRIVER={SQL Server Native Client 11.0};
                                               server=", my_server, "; 
                                               database=", my_db, "; 
                                               uid=", my_username, "; 
                                               pwd=", my_pwd))
    
    #Seleccion de datos de entrenamiento
    QuerySql <- paste0("SELECT AREA_P AREA FROM TALHAO WITH(NOLOCK) WHERE FAZ = '", Hda, "' AND TAL = '", ste,"'", sep="")
    
    data <- sqlQuery(conexionSIAGRI, QuerySql)
    
    odbcClose(conexionSIAGRI)
    
    return(data)
    
  }
  data<-datosArea(hda,ste)
  data[1,1] <- 0
  data[1,1] <- as.numeric(areaR)
  
  shp <- shape
  ph_prom<-round(mean(shp$ph),2)
  prop_fracc <- prop_fracc 
  
  tabla_recomendacion<-data.frame()
  
  if((sum(proporcion[1, ]) + sum(proporcion[2, ]))==0){
    if(ph_prom <= 7.2) {
      a <- which(Efi$Fertilizante == fert[1])
      a1 <- which(Efi$Fertilizante == fert1[1])
      factor <- (prop_fracc / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (abs(1 - prop_fracc) / as.numeric(Efi$Eficiencia.de.absorcion[a1]))
      unidades <- round(mean(shp$Dosis) * as.numeric(factor), 2)
      if (unidades < 138){
        b<-0
        unidades <- 138
      }else{
        if (unidades > 186){
          b <- unidades - 186
          unidades <- 186
        }else{
          unidades <- unidades
          b<-0
        }
      }
      tabla_recomendacion[1,1] <- unidades * prop_fracc
      tabla_recomendacion[1,2] <- round(tabla_recomendacion[1,1] / as.numeric(Efi$Porcentaje.de.concentracion[a]), 2)
      tabla_recomendacion[1,3] <- round(tabla_recomendacion[1,2] * as.numeric(data[1,1]), 2)
      tabla_recomendacion[1,4] <- round(tabla_recomendacion[1,3] /50 , 2)
      tabla_recomendacion[1,5] <- round(tabla_recomendacion[1,3] * as.numeric(Efi$Costo.Kg[a]), 2)
      tabla_recomendacion[1,6] <- b
      tabla_recomendacion[1,7] <- 1
      tabla_recomendacion[2,1] <- unidades * abs(1 - prop_fracc)
      tabla_recomendacion[2,2] <- round(tabla_recomendacion[2,1] / as.numeric(Efi$Porcentaje.de.concentracion[a1]), 2)
      tabla_recomendacion[2,3] <- round(tabla_recomendacion[2,2] * as.numeric(data[1,1]), 2)
      tabla_recomendacion[2,4] <- round(tabla_recomendacion[2,3] / 50, 2)
      tabla_recomendacion[2,5] <- round(tabla_recomendacion[2,3] * as.numeric(Efi$Costo.Kg[a1]), 2)
      tabla_recomendacion[2,6] <- b
      tabla_recomendacion[2,7] <- 2
      names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo", "Fraccion")
      if (fert[1] == fert1[1]){
        row.names(tabla_recomendacion) <- c(fert[1], paste0(fert1[1], "_1"))
      }else{
        row.names(tabla_recomendacion) <- c(fert[1], fert1[1])
      }
    }else{
      if(ph_prom>7.2 & ph_prom<=7.6){
        a <- which(Efi$Fertilizante == fert[1])
        a1 <- which(Efi$Fertilizante == fert1[1])
        factor <- (prop_fracc / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (abs(1 - prop_fracc) / as.numeric(Efi$Eficiencia.de.absorcion[a1]))
        unidades <- round(mean(shp$Dosis) * as.numeric(factor), 2)
        if (unidades < 138){
          b<-0
          unidades <- 138
        }else{
          if (unidades > 186){
            b <- unidades - 186
            unidades <- 186
          }else{
            unidades <- unidades
            b<-0
          }
        }
        tabla_recomendacion[1,1] <- unidades * prop_fracc
        tabla_recomendacion[1,2] <- round(tabla_recomendacion[1,1] / as.numeric(Efi$Porcentaje.de.concentracion[a]), 2)
        tabla_recomendacion[1,3] <- round(tabla_recomendacion[1,2] * as.numeric(data[1,1]), 2)
        tabla_recomendacion[1,4] <- round(tabla_recomendacion[1,3] /50 , 2)
        tabla_recomendacion[1,5] <- round(tabla_recomendacion[1,3] * as.numeric(Efi$Costo.Kg[a]), 2)
        tabla_recomendacion[1,6] <- b
        tabla_recomendacion[1,7] <- 1
        tabla_recomendacion[2,1] <- unidades * abs(1 - prop_fracc)
        tabla_recomendacion[2,2] <- round(tabla_recomendacion[2,1] / as.numeric(Efi$Porcentaje.de.concentracion[a1]), 2)
        tabla_recomendacion[2,3] <- round(tabla_recomendacion[2,2] * as.numeric(data[1,1]), 2)
        tabla_recomendacion[2,4] <- round(tabla_recomendacion[2,3] / 50, 2)
        tabla_recomendacion[2,5] <- round(tabla_recomendacion[2,3] * as.numeric(Efi$Costo.Kg[a1]), 2)
        tabla_recomendacion[2,6] <- b
        tabla_recomendacion[2,7] <- 2
        names(tabla_recomendacion)<-c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo", "Fraccion")
        if (fert[1] == fert1[1]){
          row.names(tabla_recomendacion) <- c(fert[1], paste0(fert1[1], "_1"))
        }else{
          row.names(tabla_recomendacion) <- c(fert[1], fert1[1])
        }
        
      }else{
        if(ph_prom>7.6 && ph_prom<=8.3){
          list_f <- list(fert, fert1)
          conta <- 1
          unidades <- 0
          for (f in list_f){
            if (conta == 1){
              prop_f <- prop_fracc
            }else{
              prop_f <- abs(1 - prop_fracc)
            }
            a <- which(Efi$Fertilizante == f[1])
            a1 <- which(Efi$Fertilizante == f[2])
            factor <- ((prop_f * 0.5) / as.numeric(Efi$Eficiencia.de.absorcion[a])) + ((prop_f * 0.5) / as.numeric(Efi$Eficiencia.de.absorcion[a1]))
            unidades <- round((mean(shp$Dosis)) * as.numeric(factor), 2) + unidades
            conta <- conta + 1
          }
          
          if (unidades < 138){
            unidades <- 138
            b <- 0
          }else{
            if (unidades > 186){
              b <- unidades - 186
              unidades <- 186
            }else{
              unidades <- unidades
              b <- 0
            }
          }
          
          conta <- 1
          fer_n <- c(fert, fert1)
          for (i in 1 : 4) {
            if (conta == 1 | conta == 2){
              prop_f <- prop_fracc
              fracc <- 1
            }else{
              prop_f <- abs(1 - prop_fracc)
              fracc <- 2
            }
            dosis <- unidades * prop_f
            tabla_recomendacion[i,1] <- round(dosis * 0.5, 2)
            tabla_recomendacion[i,2] <- round(tabla_recomendacion[i,1] / as.numeric(Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fer_n[i])]), 2)
            tabla_recomendacion[i,3] <- round(tabla_recomendacion[i,2] * as.numeric(data[1,1]), 2)
            tabla_recomendacion[i,4] <- round(tabla_recomendacion[i,3] / 50, 2)
            tabla_recomendacion[i,5] <- round(tabla_recomendacion[i,2] * as.numeric(Efi$Costo.Kg[which(Efi$Fertilizante==fer_n[i])]), 2)
            tabla_recomendacion[i,6] <- b
            tabla_recomendacion[i,7] <- fracc
            
            conta <- conta + 1
          }
          names(tabla_recomendacion) <- c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo", "Fraccion")
          row.names(tabla_recomendacion) <- c(fert, paste0(fert1, "_1"))
        }else{
          fert <- c("SAM", "Nitrax")
          fert1 <- c("SAM", "Nitrax")
          list_f <- list(fert, fert1)
          conta <- 1
          unidades <- 0
          for (f in list_f){
            if (conta == 1){
              prop_f <- prop_fracc
            }else{
              prop_f <- abs(1 - prop_fracc)
            }
            a <- which(Efi$Fertilizante == f[1])
            a1 <- which(Efi$Fertilizante == f[2])
            factor <- ((prop_f * 0.6) / as.numeric(Efi$Eficiencia.de.absorcion[a])) + ((prop_f * 0.4) / as.nuemric(Efi$Eficiencia.de.absorcion[a1]))
            unidades <- round((mean(shp$Dosis)) * as.numeric(factor), 2) + unidades
            conta <- conta + 1
          }
          
          if (unidades < 138){
            unidades <- 138
            b <- 0
          }else{
            if (unidades > 186){
              b <- unidades - 186
              unidades <- 186
            }else{
              unidades <- unidades
              b <- 0
            }
          }
          
          conta <- 1
          fer_n <- c(fert, fert1)
          for (i in 1 : 4) {
            if (conta == 1 | conta == 2){
              prop_f <- prop_fracc
              fracc <- 1
            }else{
              prop_f <- abs(1 - prop_fracc)
              fracc <- 2
            }
            dosis <- unidades * prop_f
            if (fer_n[i] == "SAM"){
              tabla_recomendacion[i,1] <- round(dosis * 0.6, 2)
            }else{
              tabla_recomendacion[i,1] <- round(dosis * 0.4, 2)
            }
            
            tabla_recomendacion[i,2] <- round(tabla_recomendacion[i,1] / as.numeric(Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fer_n[i])]), 2)
            tabla_recomendacion[i,3] <- round(tabla_recomendacion[i,2] * as.numeric(data[1,1]), 2)
            tabla_recomendacion[i,4] <- round(tabla_recomendacion[i,3] / 50, 2)
            tabla_recomendacion[i,5] <- round(tabla_recomendacion[i,2] * as.numeric(Efi$Costo.Kg[which(Efi$Fertilizante==fer_n[i])]), 2)
            tabla_recomendacion[i,6] <- b
            tabla_recomendacion[i,7] <- fracc
          }
          names(tabla_recomendacion) <- c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo", "Fraccion")
          row.names(tabla_recomendacion) <- c(fert, paste0(fert1, "_1"))
        }
      }
    }
  }else{
    fert <- names(proporcion)[which(proporcion [1, ] != 0)]
    fert1 <- names(proporcion)[which(proporcion [2, ] != 0)]
    fert_f <- proporcion[1, which(proporcion [1, ] != 0)]
    fert1_f <- proporcion[2, which(proporcion [2, ] != 0)]
    
    list_f <- list(fert, fert1)
    list_fac <- list(fert_f, fert1_f)
    conta <- 1
    unidades <- 0
    for (f in list_f){
      if (conta == 1){
        prop_f <- prop_fracc
      }else{
        prop_f <- abs(1 - prop_fracc)
      }
      if (length(f) == 1){
        a <- which(Efi$Fertilizante == f[1])
        a_f <- as.numeric(list_fac[[conta]][1])
        factor <- ((prop_f * a_f) / as.numeric(Efi$Eficiencia.de.absorcion[a]))
        unidades <- round((mean(shp$Dosis)) * as.numeric(factor), 2) + unidades
        print(unidades)
      }else{
        a <- which(Efi$Fertilizante == f[1])
        a1 <- which(Efi$Fertilizante == f[2])
        a_f <- as.numeric(list_fac[[conta]][1])
        a1_f <- as.numeric(list_fac[[conta]][2])
        factor <- ((prop_f * a_f) / as.numeric(Efi$Eficiencia.de.absorcion[a])) + ((prop_f * a1_f) / as.numeric(Efi$Eficiencia.de.absorcion[a1]))
        unidades <- round((mean(shp$Dosis)) * as.numeric(factor), 2) + unidades
      }
      conta <- conta + 1
    }
    
    if (unidades < 138){
      unidades <- 138
      b <- 0
    }else{
      if (unidades > 186){
        b <- unidades - 186
        unidades <- 186
      }else{
        unidades <- unidades
        b <- 0
      }
    }
    
    conta <- 1
    fer_n <- c(fert, fert1)
    fer_nf <- c(fert_f, fert1_f)
    if (length(fer_n) == 2){
      for (i in 1 : 2) {
        if (conta == 1){
          prop_f <- prop_fracc
          fracc <- 1
        }else{
          prop_f <- abs(1 - prop_fracc)
          fracc <- 2
        }
        dosis <- unidades * prop_f
        print(dosis)
        tabla_recomendacion[i,1] <- round(dosis, 2)
        tabla_recomendacion[i,2] <- round(tabla_recomendacion[i,1] / as.numeric(Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fer_n[i])]), 2)
        tabla_recomendacion[i,3] <- round(tabla_recomendacion[i,2] * as.numeric(data[1,1]), 2)
        tabla_recomendacion[i,4] <- round(tabla_recomendacion[i,3] / 50, 2)
        tabla_recomendacion[i,5] <- round(tabla_recomendacion[i,2] * as.numeric(Efi$Costo.Kg[which(Efi$Fertilizante==fer_n[i])]), 2)
        tabla_recomendacion[i,6] <- b
        tabla_recomendacion[i,7] <- fracc
        conta <- conta + 1
      }
    }else{
      for (i in 1 : 4) {
        if (conta == 1 | conta == 2){
          prop_f <- prop_fracc
          fracc <- 1
        }else{
          prop_f <- abs(1 - prop_fracc)
          fracc <- 2
        }
        dosis <- unidades * prop_f
        tabla_recomendacion[i,1] <- round(dosis * as.numeric(fer_nf[i]), 2)
        tabla_recomendacion[i,2] <- round(tabla_recomendacion[i,1] / as.numeric(Efi$Porcentaje.de.concentracion[which(Efi$Fertilizante==fer_n[i])]), 2)
        tabla_recomendacion[i,3] <- round(tabla_recomendacion[i,2] * as.numeric(data[1,1]), 2)
        tabla_recomendacion[i,4] <- round(tabla_recomendacion[i,3] / 50, 2)
        tabla_recomendacion[i,5] <- round(tabla_recomendacion[i,2] * as.numeric(Efi$Costo.Kg[which(Efi$Fertilizante==fer_n[i])]), 2)
        tabla_recomendacion[i,6] <- b
        tabla_recomendacion[i,7] <- fracc
        conta <- conta + 1
      }
    }
    
    names(tabla_recomendacion) <- c("Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo", "Fraccion")
    row.names(tabla_recomendacion) <- c(fert, paste0(fert1, "_1"))
  }
  
  return(as.data.frame(tabla_recomendacion)) 
  
}

hist<-function(varied,hac,ste){
  
  datosQuery <- function(fecha_ini,fecha_fin) {
    
    library(RODBC)
    
    my_server = "AGROIPSAVDB01\\PROD"
    my_db = "SIAGRI_AG"
    my_username = "sg_interf"
    my_pwd = "PIFAC4598"
    
    conexionSIAGRI <- odbcDriverConnect(paste0("DRIVER={SQL Server Native Client 11.0};
                                                server=", my_server, "; 
                                                database=", my_db, "; 
                                                uid=", my_username, "; 
                                                pwd=", my_pwd))
    
    #Seleccion de datos de entrenamiento
    #QuerySql <- paste0("SELECT FAZ HACIENDA,TAL SUERTE,AREA_P AREA, TCC_ULTC TCH,DBO.GET_VARIEDAD(VARIEDADE) VARIEDAD,ZONA_AGROECOLOGICA, EDAD_ULTCOL EDAD FROM HISTORIA WITH(NOLOCK) WHERE FAZ = '",Hda, "' AND TAL = '", ste,"'",sep="")
    QuerySql <- paste0("SELECT FAZ HACIENDA,TAL SUERTE,AREA_P AREA, TCC_ULTC TCH,TIPO_CULT TIPO_CULTIVO,DBO.GET_VARIEDAD(VARIEDADE) VARIEDAD,ZONA_AGROECOLOGICA, EDAD_ULTCOL EDAD, ESTAGIO CORTE,PERIODO_LIQ PERIODO FROM HISTORIA WITH(NOLOCK) WHERE PERIODO_LIQ >='",fecha_ini,"'AND PERIODO_LIQ <='",fecha_fin,"'" ,sep="")
    
    sqlQuery(conexionSIAGRI, QuerySql)
    
  }
  
  ini<-paste0(year(Sys.Date())-6,0,1)
  fin<-paste0(year(Sys.Date()),0,month(Sys.Date()))
  bdh<-datosQuery(ini,fin)
  bdh$HACIENDA<-paste0(0,bdh$HACIENDA)
  bdh<-bdh[-which(substr(bdh$HACIENDA,0,2)!="08"),]
  
  #bdh<-read_excel("C:/Users/dfperdomo/Desktop/Analisis_estadistico/Aplicacion_fertilizacion/BD_historico.xls")
  
  bdhs<-subset(bdh,bdh$HACIENDA==hac & bdh$SUERTE==ste)
  corte<-bdhs$CORTE[nrow(bdhs)]
  zona<-bdhs$ZONA_AGROECOLOGICA[nrow(bdhs)]
  tipoc<-bdhs$TIPO_CULTIVO[nrow(bdhs)]
  vrd<-bdhs$VARIEDAD[nrow(bdhs)]
  bdhv<-subset(bdh,bdh$VARIEDAD==vrd & bdh$CORTE==corte & bdh$ZONA_AGROECOLOGICA==zona & bdh$TIPO_CULTIVO==tipoc)
  
  lim_sup<-mean(bdhv$TCH)+(2*sd(bdhv$TCH))
  lim_inf<-mean(bdhv$TCH)-(2*sd(bdhv$TCH))
  bdhv<-subset(bdhv,bdhv$TCH<=lim_sup & bdhv$TCH>=lim_inf)
  
  historico<-data.frame()
  historico[1,1]<-round(mean(bdhs$TCH),2)
  historico[1,2]<-round(max(bdhs$TCH),2)
  historico[1,3]<-round(min(bdhs$TCH),2)
  historico[1,4]<-round(sd(bdhs$TCH),2)
  historico[2,1]<-round(mean(bdhv$TCH),2)
  historico[2,2]<-round(max(bdhv$TCH),2)
  historico[2,3]<-round(min(bdhv$TCH),2)
  historico[2,4]<-round(sd(bdhv$TCH),2)
  
  names(historico)<-c("Promedio","Maximo","Minimo","Desv. estandar")
  rownames(historico)<-c("Estadisticos por suerte","Estadisticos por caracteristicas similares")
  historico<-as.data.frame(historico)
  
  return(historico)
}

BD_hisotrica <- function(){
  
  datosQuery <- function(fecha_ini,fecha_fin) {
    
    library(RODBC)
    
    my_server = "AGROIPSAVDB01\\PROD"
    my_db = "SIAGRI_AG"
    my_username = "sg_interf"
    my_pwd = "PIFAC4598"
    
    conexionSIAGRI <- odbcDriverConnect(paste0("DRIVER={SQL Server Native Client 11.0};
                                                server=", my_server, "; 
                                                database=", my_db, "; 
                                                uid=", my_username, "; 
                                                pwd=", my_pwd))
    
    #Seleccion de datos de entrenamiento
    #QuerySql <- paste0("SELECT FAZ HACIENDA,TAL SUERTE,AREA_P AREA, TCC_ULTC TCH,DBO.GET_VARIEDAD(VARIEDADE) VARIEDAD,ZONA_AGROECOLOGICA, EDAD_ULTCOL EDAD FROM HISTORIA WITH(NOLOCK) WHERE FAZ = '",Hda, "' AND TAL = '", ste,"'",sep="")
    QuerySql <- paste0("SELECT FAZ HACIENDA,TAL SUERTE,AREA_P AREA, TCC_ULTC TCH,TIPO_CULT TIPO_CULTIVO,DBO.GET_VARIEDAD(VARIEDADE) VARIEDAD,ZONA_AGROECOLOGICA, EDAD_ULTCOL EDAD, ESTAGIO CORTE,PERIODO_LIQ PERIODO FROM HISTORIA WITH(NOLOCK) WHERE PERIODO_LIQ >='",fecha_ini,"'AND PERIODO_LIQ <='",fecha_fin,"'" ,sep="")
    
    sqlQuery(conexionSIAGRI, QuerySql)
    
  }
  
  ini<-paste0(year(Sys.Date())-6,0,1)
  fin<-paste0(year(Sys.Date()),0,month(Sys.Date()))
  bdh<-datosQuery(ini,fin)
  bdh$HACIENDA<-paste0(0,bdh$HACIENDA)
  bdh<-bdh[-which(substr(bdh$HACIENDA,0,2)!="08"),]
  
  return(bdh)
}

TCHmax <- function(hac,ste, bdh){
  
  bdhs <- subset(bdh, bdh$HACIENDA == hac & bdh$SUERTE == ste)
  
  if(length(which(bdhs$CORTE == 0)) == 0){
    tch_maximo <- max(bdhs$TCH)
  }else{
    vec <- which(bdhs$CORTE >= 0)
    tch_maximo <- max(bdhs$TCH[vec])
  }
  
  return(tch_maximo)
}

RCMP<-function(tablones, hacienda, suerte, variedad, compost, vinaza, TCHE, porce_comp, porc_vinaza){
  
  ##Archivos planos
  Efi<-read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Tabla_eficiencia.csv",sep = ";")
  DA_ref<-read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/DA.csv",sep = ";")
  #inventario_muestreo <- read_excel("//pncamp24/discex/MAPAS/Variabilidad_Quimica/Datos_muestreo_optimizado/Inventario area muestreo optimizado.xlsx", 
  #                                  sheet = "final")
  inventario_muestreo <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Datos_muestreo_optimizado/Inventario area muestreo optimizado.xlsx",#---------------------------------------FALTA ACCESO A PNSIG01>>>SE USÓ LOCAL
                                    sheet = "final")
  
  ##Archivos shape puntos de muestreo y archivos planos semivariograma
  if(inventario_muestreo$`%`[inventario_muestreo$Cod==hacienda]==1){
    pts_mstr<-readOGR("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Datos_muestreo_optimizado/Ptos_actual.shp")#------------------------------------------------------------------------------FALTA ACCESO A PNSIG01>>>SE USÓ LOCAL
    pts_mstr <- remove.duplicates(pts_mstr, zero = 1, remove.second = TRUE)
    param <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Tabla_parametros_kriging.xlsx")
    param_subset <- subset(param, param$Hacienda == hacienda)
  }else{
    param <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Datos_muestreo_optimizado/Tabla variables interpolacion_Analisis Lab_V2.xlsx")#-----------------------------------------FALTA ACCESO A PNSIG01>>>SE USÓ LOCAL
    pts_mstr<-readOGR("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Fertilizacion shp/suelos/Puntos de muestreo/As_Grilla_General_muestreo1.shp")
    pts_mstr <- remove.duplicates(pts_mstr, zero = 1, remove.second = TRUE)
    param_subset<-param[,c(1,2,4,5,10,11,12)]
    names(param_subset)<-c("Variable","Propiedad","Unidad","Distancia","Nugget","Silla","Rango")
  }
  
  ##Archivos shape hacienda, suerte y tablones
  capa_hacienda<-readOGR("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Fertilizacion shp/hda.shp")#------------------------------------------------------------------------------------------------------------FALTA ACCESO A PNSIG01>>>SE USÓ LOCAL
  capa_suerte<-readOGR("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Fertilizacion shp/ste.shp")#--------------------------------------------------------------------------------------------------------------FALTA ACCESO A PNSIG01>>>SE USÓ LOCAL
  #capa_suerte<-readOGR("C:/Users/dfperdomo/Desktop/ste.shp")
  #capa_suerte<-readOGR("//pnsig01/compartida/Diego Perdomo/Cartografia/ste2.shp")
  
  ### Union de meses del archivo de control de mapas de productividad
  CM<-data.frame()
  meses<-c("ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE")
  for (t in 1:12) {
    #CM1 <- read_excel("C:/Users/dfperdomo/Documents/Archivos/CONTROL DE MAPAS GENERAL_2023.xlsx", 
    #                  sheet = meses[t])
    #C:/Users/cccoralc/Documents/0/6. FERTILIZACION TV/csv a cargar/CONTROL DE MAPAS GENERAL_2025.xlsx
    CM1 <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/CONTROL DE MAPAS GENERAL_2025.xlsx", 
                      sheet = meses[t])
    CM<-rbind(CM,CM1)
    CM1<-NULL
    
  }
  
  CM$hdaste<-paste0(CM$HACIENDA,CM$SUERTE)
  
  ####
  
  if(length(which(tablones@data$Hac==hacienda & tablones@data$Ste==suerte))==0 || length(capa_suerte[which(capa_suerte$Hac==hacienda & capa_suerte$Ste==suerte),]) == 0){
    return("")
  }else{
    if(length(CM$Dif_Area[which(CM$HACIENDA==hacienda & CM$SUERTE==suerte)])==0){
      ver <- 1
    }else{
      pos <- length(CM$Dif_Area[which(CM$HACIENDA==hacienda & CM$SUERTE==suerte)])
      ver<-CM$Dif_Area[which(CM$HACIENDA==hacienda & CM$SUERTE==suerte)][pos]
    }
    
    y <- as.character(year(Sys.Date()))
    #y <- "2024"                                   ----------------------------SIMMPRO MAPAS DE PRODUCTIVIDAD----------------------------
    if (file.exists(paste0("D:/Users/sacorreac/OneDrive - Sector Agro/AP/9. MAPAS DE PRODUCTIVIDAD/",hacienda,"/",y,"/",suerte,"/",hacienda,suerte,".shp")) & ver<0.5 & !is.na(ver)){
      
      ####Interpolacion MO y pH####
      
      poli<-capa_hacienda[which(capa_hacienda@data$Hac==hacienda),]      
      data<-raster::intersect(pts_mstr,poli)@data
      data<-cbind(data,raster::intersect(pts_mstr,poli)@coords) 
      
      
      ## Asignar el valo de DA seg?n la textura
      pts_hac <- raster::intersect(pts_mstr,poli)
      pts_hac@data$DA<-NA
      for (n in (1:nrow(pts_hac@data))) {
        if(is.na(pts_hac@data$tex[n])){
          a<-which(DA_ref$Textura==pts_hac@data$tex[n-1])
        }else{
          a<-which(DA_ref$Textura==pts_hac@data$tex[n])
        }
        
        pts_hac@data$DA[n]<-DA_ref$DA[a]
      }
      
      ext = gBuffer(poli, width = 50, quadsegs = 1)@bbox
      tam_cell = 20
      #geodatos_grid=expand.grid(Este=seq((ext[1,1]-500),(ext[1,2]+500),by=tam_cell), Norte=seq((ext[2,1]-500),(ext[2,2]+500),by=tam_cell))
      geodatos_grid=expand.grid(Este=seq(ext[1,1],ext[1,2],by=tam_cell), Norte=seq(ext[2,1],ext[2,2],by=tam_cell))
      cap_ras<-list()
      
      #####Mapa de productividad
      geodatos_grid1<-geodatos_grid
      names(geodatos_grid1)<-c("x","y")
      coordinates(geodatos_grid1) <- ~x+y
      pts_prod <- readOGR(paste0("D:/9. MAPAS DE PRODUCTIVIDAD/",hacienda,"/",y,"/",suerte,"/",hacienda,suerte,".shp"))#-------------------SIMPRO MAPAS DE PRODUCTIVIDAD
      suerte_poli<-capa_suerte[which(capa_suerte$Hac==hacienda & capa_suerte$Ste==suerte),]
      grid_prod<-raster::intersect(geodatos_grid1,gBuffer(suerte_poli, width = 50, quadsegs = 1))
      gridded(grid_prod) <- TRUE
      #idw_prod =  gstat::idw(pts_prod@data$Prod_New~1, pts_prod, newdata=grid_prod,nmax = 20,idp=0.5)
      idw_prod = gstat(formula = Prod_New ~ 1, # intercept only model
                       data = pts_prod, 
                       nmax = 20, 
                       set = list(idp = 0.5))
      idw_prod1 <- predict(object = idw_prod,
                           newdata = grid_prod)
      
      TCHE <- as.numeric(TCHE)
      if((mean(idw_prod1@data$var1.pred)-TCHE)<0){
        idw_prod1@data$var1.pred<-idw_prod1@data$var1.pred+abs(mean(idw_prod1@data$var1.pred)-TCHE)
      }else{
        idw_prod1@data$var1.pred<-idw_prod1@data$var1.pred-abs(mean(idw_prod1@data$var1.pred)-TCHE)
      }
      
      ## Interpolaci?n con IDW de densidad aparente
      idw_da = gstat(formula = DA ~ 1, # intercept only model
                     data = pts_hac, 
                     nmax = 20, 
                     set = list(idp = 0.5))
      idw_da1 <- predict(object = idw_da,
                         newdata = grid_prod)
      
      #idw_da1<-raster(idw_da1)
      #da<-rasterToPolygons(idw_da1,dissolve = T)
      da<-idw_da1
      RN1<-idw_prod1
      
      #PCA<-(10000*DA*0.2)*1000
      ####Requerimiento de Nitrogeno####
      fa_v <- Efi_variedades$Fa_variedad[which(Efi_variedades == variedad)]
      idw_prod1@data$var1.pred <- idw_prod1@data$var1.pred * fa_v
      
      cont<-1
      for (m in c("ar","ph","mo")) {
        a<-which(param_subset$Propiedad==m)
        geodatos = as.geodata(data,coords.col = (ncol(data)-1):ncol(data),data.col = which(colnames(data)==m))
        geodatos_ko <- krige.conv(geodatos,locations = grid_prod@coords, krige = krige.control(nugget = as.numeric(param_subset[a,5]), trend.d = "cte",trend.l = "cte",
                                                                                               cov.pars = c(sigmasq=as.numeric(param_subset[a,6]),phi=as.numeric(param_subset[a,7]))))
        raster_cre=rasterFromXYZ(cbind(grid_prod@coords,geodatos_ko$predict))
        #writeOGR(da, dsn="C:/Users/dfperdomo/Desktop/Analisis_estadistico/Aplicacion_fertilizacion/AP_Fertilizacion", layer=m,driver = "ESRI Shapefile",overwrite_layer = TRUE)
        #raster::writeRaster(raster_cre,paste0("C:/Users/dfperdomo/Desktop/Analisis_estadistico/Aplicacion_fertilizacion/AP_Fertilizacion/",m,".tif"))
        raster_mask = raster::mask(raster_cre, gBuffer(suerte_poli, width = 50, quadsegs = 1))
        #crs(raster_mask) <- CRS("+init=epsg:21896")
        cap_ras[cont]<-raster_mask
        cont<-cont+1
      }
      
      idw_prod1<-as(idw_prod1, "SpatialPolygonsDataFrame")
      da<-as(da, "SpatialPolygonsDataFrame")
      
      idw_prod1@data$ar<-raster::extract(cap_ras[[1]],idw_prod1)
      idw_prod1@data$ph<-raster::extract(cap_ras[[2]],idw_prod1)
      idw_prod1@data$mo<-raster::extract(cap_ras[[3]],idw_prod1)
      
      idw_prod1<-raster::crop(idw_prod1,tablones[which(tablones$Hac==hacienda & tablones$Ste==suerte),])
      da<-raster::crop(da,tablones[which(tablones$Hac==hacienda & tablones$Ste==suerte),])
      
      idw_prod1@data$ar<-as.numeric(idw_prod1@data$ar)
      idw_prod1@data$ph<-as.numeric(idw_prod1@data$ph)
      idw_prod1@data$mo<-as.numeric(idw_prod1@data$mo)
      
      idw_prod1@data$area<-0
      for (t in 1:nrow(idw_prod1)) {
        idw_prod1@data$area[t]<-idw_prod1@polygons[[t]]@area
      }
      
      
      ####Nitrogeno Compost y Vinaza####
      #NC<-(compost*1000*porce_comp/100)/2
      NC<-((compost * 1000) * (porce_comp / 100)) / 2
      NV <- ((vinaza * 1000) * (porc_vinaza / 100)) / 2
      
      idw_prod1@data$Dosis<-0
      ####NITROGENO TOTAL KG####
      for (l in 1:nrow(idw_prod1@data)) {
        idw_prod1@data$Dosis[l]<-(idw_prod1@data$mo[l]/100)*(((idw_prod1@data$area[l])*da$var1.pred[l]*0.2)*1000)
        
        if(idw_prod1@data$ph[l]>=6 & idw_prod1@data$ph[l]<7.3){
          idw_prod1@data$Dosis[l]<-((idw_prod1@data$Dosis[l]*0.06*0.02)+NC+NV)
        }else{
          if(idw_prod1@data$ph[l]>=7.3 & idw_prod1@data$ph[l]<=7.8){
            idw_prod1@data$Dosis[l]<-((idw_prod1@data$Dosis[l]*0.05*0.015)+NC+NV)
          }else{
            idw_prod1@data$Dosis[l]<-((idw_prod1@data$Dosis[l]*0.04*0.01)+NC+NV)
          }
          
        }
        idw_prod1@data$Dosis[l]<-idw_prod1@data$var1.pred[l]-idw_prod1@data$Dosis[l]
      }
      
      
      mo_promedio<-round(mean(idw_prod1@data$mo),2)
      ph_promedio<-round(mean(idw_prod1@data$ph),2)
      DA_promedio<-round(mean(da$var1.pred),2)
      
      # ##Escalar el datos con el promedio
      # PCA<-(10000*DA_promedio*0.2)*1000
      # ####Requerimiento de Nitrogeno####
      # RN<-TCHE*0.86
      # MOKG_p<-(mo_promedio*PCA)/100
      # ####NITROGENO TOTAL KG####
      # 
      # if(ph_promedio>=6 & ph_promedio<7.3){
      #   MOKG_p<-(MOKG_p*0.06*0.02)+NC+NV 
      # }else{
      #   if(ph_promedio>=7.3 & ph_promedio<=7.8){
      #     MOKG_p<-(MOKG_p*0.05*0.015)+NC+NV
      #   }else{
      #     MOKG_p<-(MOKG_p*0.04*0.01)+NC+NV
      #   }  
      # }
      # MOKG_p<-RN-MOKG_p
      
      MOKG2<-idw_prod1
      
    }else{
      #PCA<-(10000*DA*0.2)*1000
      ####Requerimiento de Nitrogeno####
      fa_v <- Efi_variedades$Fa_variedad[which(Efi_variedades == variedad)]
      RN <- as.numeric(TCHE) * fa_v
      
      ####Interpolacion MO y pH####
      
      poli<-capa_hacienda[which(capa_hacienda@data$Hac==hacienda),]
      data<-raster::intersect(pts_mstr,poli)@data
      data<-cbind(data,raster::intersect(pts_mstr,poli)@coords) 
      
      
      ## Asignar el valo de DA seg?n la textura
      pts_hac<-raster::intersect(pts_mstr,poli)
      pts_hac@data$DA<-NA
      for (n in (1:nrow(pts_hac@data))) {
        if(is.na(pts_hac@data$tex[n])){
          a<-which(DA_ref$Textura==pts_hac@data$tex[n-1])
        }else{
          a<-which(DA_ref$Textura==pts_hac@data$tex[n])
        }
        
        pts_hac@data$DA[n]<-DA_ref$DA[a]
      }
      
      ext = gBuffer(poli, width = 50, quadsegs = 1)@bbox
      tam_cell = 20
      #geodatos_grid=expand.grid(Este=seq((ext[1,1]-500),(ext[1,2]+500),by=tam_cell), Norte=seq((ext[2,1]-500),(ext[2,2]+500),by=tam_cell))
      geodatos_grid=expand.grid(Este=seq(ext[1,1],ext[1,2],by=tam_cell), Norte=seq(ext[2,1],ext[2,2],by=tam_cell))
      cap_ras<-list()
      
      geodatos_grid1<-geodatos_grid
      names(geodatos_grid1)<-c("x","y")
      coordinates(geodatos_grid1) <- ~x+y
      suerte_poli<-capa_suerte[which(capa_suerte$Hac==hacienda & capa_suerte$Ste==suerte),]
      grid_prod<-raster::intersect(geodatos_grid1,gBuffer(suerte_poli, width = 50, quadsegs = 1))
      gridded(grid_prod) <- TRUE
      ## Interpolaci?n con IDW de densidad aparente
      idw_da = gstat(formula = DA ~ 1, # intercept only model
                     data = pts_hac, 
                     nmax = 20, 
                     set = list(idp = 0.5))
      idw_da1 <- predict(object = idw_da,
                         newdata = grid_prod)
      
      #idw_da1<-raster(idw_da1)
      #da<-rasterToPolygons(idw_da1,dissolve = T)
      da<-idw_da1
      
      cont<-1
      for (m in c("ar","ph","mo")) {
        a<-which(param_subset$Propiedad==m)
        geodatos = as.geodata(data,coords.col = (ncol(data)-1):ncol(data),data.col = which(colnames(data)==m))
        geodatos_ko <- krige.conv(geodatos,locations = grid_prod@coords, krige = krige.control(nugget = as.numeric(param_subset[a,5]), trend.d = "cte",trend.l = "cte",
                                                                                               cov.pars = c(sigmasq=as.numeric(param_subset[a,6]),phi=as.numeric(param_subset[a,7]))))
        
        raster_cre=rasterFromXYZ(cbind(grid_prod@coords,geodatos_ko$predict))
        raster_mask = raster::mask(raster_cre, gBuffer(suerte_poli, width = 50, quadsegs = 1))
        #crs(raster_mask) <- CRS("+init=epsg:21896")
        cap_ras[cont]<-raster_mask
        cont<-cont+1
      }
      
      ####Materia Organica KG####
      da<-as(da, "SpatialPolygonsDataFrame")
      
      da@data$ar<-raster::extract(cap_ras[[1]],da)
      da@data$ph<-raster::extract(cap_ras[[2]],da)
      da@data$mo<-raster::extract(cap_ras[[3]],da)
      
      da<-raster::crop(da,tablones[which(tablones$Hac==hacienda & tablones$Ste==suerte),])
      
      da@data$ar<-as.numeric(da@data$ar)
      da@data$ph<-as.numeric(da@data$ph)
      da@data$mo<-as.numeric(da@data$mo)
      
      da@data$area<-0
      for (t in 1:nrow(da@data)) {
        da@data$area[t]<-da@polygons[[t]]@area
      }
      
      
      
      ####Nitrogeno Compost y Vinaza####
      #NC<-(compost*1000*porce_comp/100)/2
      NC <- ((compost * 1000) * (porce_comp / 100)) / 2
      NV <- ((vinaza * 1000) * (porc_vinaza / 100)) / 2
      
      
      da@data$Dosis<-0
      
      ####NITROGENO TOTAL KG####
      for (l in 1:nrow(da@data)) {
        da@data$Dosis[l]<-(da@data$mo[l]/100)*(((da@data$area[l])*da$var1.pred[l]*0.2)*1000)
        if(da@data$ph[l]>=6 & da@data$ph[l]<7.3){
          da@data$Dosis[l]<-((da@data$Dosis[l]*0.06*0.02)+NC+NV)
        }else{
          if(da@data$ph[l]>=7.3 & da@data$ph[l]<=7.8){
            da@data$Dosis[l]<-((da@data$Dosis[l]*0.05*0.015)+NC+NV)
          }else{
            da@data$Dosis[l]<-((da@data$Dosis[l]*0.04*0.01)+NC+NV)
          }  
        }
        da@data$Dosis[l]<-RN-da@data$Dosis[l]
      }
      
      
      mo_promedio<-round(mean(da@data$mo),2)
      ph_promedio<-round(mean(da@data$ph),2)
      DA_promedio<-round(mean(da$var1.pred),2)
      
      # PCA<-(10000*DA_promedio*0.2)*1000
      # ####Requerimiento de Nitrogeno####
      # MOKG_p<-(mo_promedio*PCA)/100
      # ####NITROGENO TOTAL KG####
      # 
      # if(ph_promedio>=6 & ph_promedio<7.3){
      #   MOKG_p<-(MOKG_p*0.06*0.02)+NC+NV 
      # }else{
      #   if(ph_promedio>=7.3 & ph_promedio<=7.8){
      #     MOKG_p<-(MOKG_p*0.05*0.015)+NC+NV 
      #   }else{
      #     MOKG_p<-(MOKG_p*0.04*0.01)+NC+NV 
      #   }  
      # }
      # MOKG_p<-RN-MOKG_p
      
      
      MOKG2<-da
    }
    
    
  }
  
  return(MOKG2)
}

Distrib_tolvas<-function(tabla, hda, ste, area, areaR){
  tabla_recomendacion<-data.frame()
  datosArea <- function(Hda,ste) {
    
    library(RODBC)
    
    my_server = "AGROIPSAVDB01\\PROD"
    my_db = "SIAGRI_AG"
    my_username = "sg_interf"
    my_pwd = "PIFAC4598"
    
    conexionSIAGRI <- odbcDriverConnect(paste0("DRIVER={SQL Server Native Client 11.0};
                                               server=", my_server, "; 
                                               database=", my_db, "; 
                                               uid=", my_username, "; 
                                               pwd=", my_pwd))
    
    #Seleccion de datos de entrenamiento
    QuerySql <- paste0("SELECT AREA_P AREA FROM TALHAO WITH(NOLOCK) WHERE FAZ = '", Hda, "' AND TAL = '", ste,"'", sep="")
    
    data <- sqlQuery(conexionSIAGRI, QuerySql)
    
    odbcClose(conexionSIAGRI)
    
    return(data)
    
  }
  data<-datosArea(hda,ste)
  #############################################################################################################
  ## 1 Producto
  if(nrow(tabla)==1){
    Dosis<-tabla[1,5]
    vec<-c(0,0.22,0.25,0.255,0.265,0.3,0.35,0.375,0.4,0.43,0.45,0.47,0.49,0.5,0.55,0.56,0.57,0.6,0.625,0.65,0.7,1)
    combinaciones<-expand.grid(vec,vec,vec)
    combinaciones$suma<-combinaciones$Var1+combinaciones$Var2+combinaciones$Var3
    combinaciones<-subset(combinaciones,combinaciones$suma==1)
    combinaciones$Var1<-Dosis*combinaciones$Var1
    combinaciones$Var2<-Dosis*combinaciones$Var2
    combinaciones$Var3<-Dosis*combinaciones$Var3
    
    v<-c()
    for (i in 1:nrow(combinaciones)) {
      a<-which(combinaciones[i,c(1,2,3)]<70 & combinaciones[i,c(1,2,3)]>0)
      if(length(a)>0){
        v<-c(v,i)
      }else{
        next()
      }
    }
    
    if(length(v)==0){
      combinaciones<-combinaciones
    }else{
      combinaciones<-combinaciones[-v,]
    }
    
    Autonomia<-combinaciones
    Autonomia$Var1<-500/combinaciones$Var1
    Autonomia$Var2<-300/combinaciones$Var2
    Autonomia$Var3<-300/combinaciones$Var3
    Autonomia$suma<-apply(Autonomia[,c(1,2,3)],1,min)
    
    com_final<-combinaciones[which.max(Autonomia$suma),]
    #Autonomia[which.max(Autonomia$suma),]
  }else{
    if(nrow(tabla)==2){
      ## 2 Producto
      
      dosis<-c()
      for (i in 1:2) {
        dosis<-c(dosis,tabla[i,5])
      }
      
      vec<-c(0,0.33,0.375,0.4,0.5,0.625,0.67,1)
      combinaciones<-expand.grid(vec,vec,vec)
      combinaciones$suma<-combinaciones$Var1+combinaciones$Var2+combinaciones$Var3
      combinaciones<-subset(combinaciones,combinaciones$suma==2)
      combinaciones1<-data.frame()
      
      for (i in 1:nrow(combinaciones)) {
        if(length(which(combinaciones[i,]==1))==1){
          a<-which(combinaciones[i,]==1)
          b<-setdiff(c(1,2,3),which(combinaciones[i,]==1))
          vec<-combinaciones[i,c(1,2,3)]
          vec[1,a]<-vec[1,a]*dosis[1]
          vec[1,b]<-vec[1,b]*dosis[2]
          vec$fertilizantes[1]<-paste(row.names(tabla)[1],row.names(tabla)[2],row.names(tabla)[2],sep="-")
          combinaciones1<-rbind(combinaciones1,vec)
          vec<-combinaciones[i,c(1,2,3)]
          vec[1,a]<-vec[1,a]*dosis[2]
          vec[1,b]<-vec[1,b]*dosis[1]
          vec$fertilizantes[1]<-paste(row.names(tabla)[2],row.names(tabla)[1],row.names(tabla)[1],sep="-")
          combinaciones1<-rbind(combinaciones1,vec)
        }else{
          a<-which(combinaciones[i,]==1)
          vec<-combinaciones[i,c(1,2,3)]
          vec[1,a[1]]<-dosis[2]
          vec[1,a[2]]<-dosis[1]
          vec$fertilizantes[1]<-paste(row.names(tabla)[2],row.names(tabla)[1],sep="-")
          combinaciones1<-rbind(combinaciones1,vec)
          vec<-combinaciones[i,c(1,2,3)]
          vec[1,a[1]]<-dosis[1]
          vec[1,a[2]]<-dosis[2]
          vec$fertilizantes[1]<-paste(row.names(tabla)[1],row.names(tabla)[2],sep="-")
          combinaciones1<-rbind(combinaciones1,vec)
        }
      }
      
      v<-c()
      for (i in 1:nrow(combinaciones1)) {
        a<-which(combinaciones1[i,c(1,2,3)]<60 & combinaciones1[i,c(1,2,3)]>0)
        if(length(a)>0){
          v<-c(v,i)
        }else{
          next()
        }
      }
      
      if(length(v)==0){
        combinaciones1<-combinaciones1
      }else{
        combinaciones1<-combinaciones1[-v,]
      }
      
      Autonomia<-combinaciones1
      Autonomia$Var1<-500/combinaciones1$Var1
      Autonomia$Var2<-300/combinaciones1$Var2
      Autonomia$Var3<-300/combinaciones1$Var3
      Autonomia$suma<-apply(Autonomia[,c(1,2,3)],1,min)
      
      Autonomia[which.max(Autonomia$suma),]
      com_final<-combinaciones1[which.max(Autonomia$suma),]
    }else{
      next()
    }
  }
  ############################################Generacion de tabla###################################################  
  if(length(which(com_final==0))==0){
    contador<-0
    for (s in 1:3) {
      tabla_recomendacion[s,1]<-Sys.Date()
      tabla_recomendacion[s,2]<-hda
      tabla_recomendacion[s,3]<-ste
      tabla_recomendacion[s,4]<-data[1,1]
      tabla_recomendacion[s,5]<-areaR
      tabla_recomendacion[s,6]<-round(com_final[1,s]*as.numeric(tabla_recomendacion[s,4]),2)
      tabla_recomendacion[s,7]<-round(com_final[1,s],2)
      tabla_recomendacion[s,8]<-round(com_final[1,s]*as.numeric(tabla_recomendacion[s,5]),2)
      tabla_recomendacion[s,9]<-round(com_final[1,s],2)
      tabla_recomendacion[s,10]<-ceiling(tabla_recomendacion[s,8]/50)
      tabla_recomendacion[s,11]<-ceiling(tabla_recomendacion[s,10]/as.numeric(tabla_recomendacion[s,5]))
      if(nrow(tabla)==1){
        tabla_recomendacion[s,12+contador]<-row.names(tabla)[1]
      }else{
        tabla_recomendacion[s,12+contador]<-strsplit(com_final$fertilizantes,"-")[[1]][s]
      }
      
      contador<-contador+1
    }
    names(tabla_recomendacion)<-c("Fecha","Hacienda","Suerte","Area_Cartografia","Area real","Kg/ste-Teorico","Kg/Ha-Teorico",
                                  "Kg/ste-Real","Kg/Ha-Real","Bultos/ste-Real","Bultos/ha-Real",
                                  "TOLVA 1","TOLVA 2","TOLVA 3")
  }else{
    if (length(which(com_final == 0)) == 2){
      tabla_recomendacion[1,1]<-Sys.Date()
      tabla_recomendacion[1,2]<-hda
      tabla_recomendacion[1,3]<-ste
      tabla_recomendacion[1,4]<-areaR
      tabla_recomendacion[1,5]<-data[1,1]
      tabla_recomendacion[1,6]<-round(com_final[1,1]*as.numeric(tabla_recomendacion[1,4]),2)
      tabla_recomendacion[1,7]<-round(com_final[1,1],2)
      tabla_recomendacion[1,8]<-round(com_final[1,1]*as.numeric(tabla_recomendacion[1,5]),2)
      tabla_recomendacion[1,9]<-round(com_final[1,1],2)
      tabla_recomendacion[1,10]<-ceiling(tabla_recomendacion[1,8]/50)
      tabla_recomendacion[1,11]<-ceiling(tabla_recomendacion[1,10]/as.numeric(tabla_recomendacion[1,5]))
      tabla_recomendacion[1,12]<-row.names(tabla)[1]
      tabla_recomendacion[1,13]<-0
      tabla_recomendacion[1,14]<-0
      names(tabla_recomendacion)<-c("Fecha","Hacienda","Suerte","Area_Cartografia","Area real","Kg/ste-Teorico","Kg/Ha-Teorico",
                                    "Kg/ste-Real","Kg/Ha-Real","Bultos/ste-Real","Bultos/ha-Real",
                                    "TOLVA 1","TOLVA 2","TOLVA 3")
    }else{
      contador<-0
      for (s in 1:2) {
        tabla_recomendacion[s,1]<-Sys.Date()
        tabla_recomendacion[s,2]<-hda
        tabla_recomendacion[s,3]<-ste
        tabla_recomendacion[s,4]<-as.numeric(areaR)
        tabla_recomendacion[s,5]<-data[1,1]
        tabla_recomendacion[s,6]<-round(com_final[1,s]*as.numeric(tabla_recomendacion[s,4]),2)
        tabla_recomendacion[s,7]<-round(com_final[1,s],2)
        tabla_recomendacion[s,8]<-round(com_final[1,s]*as.numeric(tabla_recomendacion[s,5]),2)
        tabla_recomendacion[s,9]<-round(com_final[1,s],2)
        tabla_recomendacion[s,10]<-ceiling(tabla_recomendacion[s,8]/50)
        tabla_recomendacion[s,11]<-ceiling(tabla_recomendacion[s,10]/as.numeric(tabla_recomendacion[s,5]))
        tabla_recomendacion[s,12+contador]<-row.names(tabla)[1]
        contador<-contador+1
      }
      tabla_recomendacion$v13 <- 0
    }
  }
  names(tabla_recomendacion)<-c("Fecha","Hacienda","Suerte","Area_Cartografia","Area real","Kg/ste-Teorico","Kg/Ha-Teorico",
                                "Kg/ste-Real","Kg/Ha-Real","Bultos/ste-Real","Bultos/ha-Real",
                                "TOLVA 1","TOLVA 2","TOLVA 3")     
  #############################################################################################################
  return(tabla_recomendacion)
}

Generar_registro<-function(hda, ste, tabla, area, obs, areaR){
  anexar<-data.frame()
  csv_anexar<-read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Salidas/Fertilizacion_registros.csv",sep=",")
  if(ncol(csv_anexar)==1){
    csv_anexar<-read.csv("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Salidas/Fertilizacion_registros.csv",sep=";")
  }else{
    csv_anexar<-csv_anexar
  }
  
  for (i in 1:nrow(tabla)) {
    anexar[i,1] <- hda
    anexar[i,2] <- ste
    anexar[i,3] <- now()
    anexar[i,4]<-row.names(tabla)[i]
    anexar[i,5]<-tabla[i,4]
    anexar[i,6]<-tabla[i,5]
    anexar[i,7]<-tabla[i,6]
    anexar[i,8]<-tabla[i,7]
    anexar[i,9]<-area
    anexar[i,10]<-areaR
    anexar[i,11]<-tabla[i,8]
    anexar[i,12]<-tabla[i,9]
    anexar[i,13]<-tabla[i,10]
    anexar[i,14]<-obs
  }
  names(anexar)<-names(csv_anexar)
  csv_anexar<-rbind(csv_anexar,anexar)
  
  #write.csv(csv_anexar,"C:/Users/dfperdomo/Desktop/Analisis_estadistico/Aplicacion_fertilizacion/AP_Fertilizacion/Fertilizacion_registros.csv",row.names = FALSE)
  return(csv_anexar)
}

shape_verion <- function(shape, recomen){
  #####Funcion para shape de verion
  dosis_mot <- recomen$`Kg/Ha-Real`
  
  prom <- mean(shape@data$Dosis)
  
  motores <- c("M1", "M2", "M3")
  cont <- 1
  
  for (i in dosis_mot) {
    dif <- i - prom
    if (dif >= 0) {
      shape@data[motores[cont]] <- shape@data$Dosis + abs(dif)
    }else {
      shape@data[motores[cont]] <- shape@data$Dosis - abs(dif)
    }
    
    
    val_m50 <- which(shape@data[motores[cont]] < 50)
    if (length(val_m50) > 0) {
      shape@data[val_m50, motores[cont]] <- 50
      prom1 <- mean(shape@data[,motores[cont]])
      dif <- i - prom1
      if (dif >= 0) {
        shape@data[motores[cont]] <- shape@data[motores[cont]] + abs(dif)
      }else {
        shape@data[motores[cont]] <- shape@data[motores[cont]] - abs(dif)
      }
    } else {
      shape@data[motores[cont]] <- shape@data[motores[cont]]
    }
    
    cont <- cont + 1
  }
  
  shape <- spTransform(shape, CRS("+init=EPSG:4326"))
  centroides <- gCentroid(shape, byid = TRUE)
  coordenadas_centroides <- coordinates(centroides)
  shape@data$Longitud <- coordenadas_centroides[, 1]
  shape@data$Latitud <- coordenadas_centroides[, 2]
  
  shape@data <- shape@data[, c(which(names(shape@data) == "area") : length(names(shape@data)))]
  
  return(shape)
  
  #writeOGR(shape, dsn = "C:/Users/dfperdomo/Downloads", layer = "poligono", driver = "ESRI Shapefile")
}

compost <- function(hacienda, suerte){
  df_compost <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Compost.xlsx")
  df_compost <- subset(df_compost, df_compost$NOME_ACTIVIDAD == "TRANSPORTE DEL COMPOST")
  a <- as.data.frame(subset(df_compost, df_compost$HACIENDA == hacienda & df_compost$SUERTE == suerte))
  if (nrow(a) == 0){
    valor_c <- 0
  }else{
    valor_c <- a$Dosis[1]
  }
  return(valor_c)
}

vinaza <- function(hacienda, suerte){
  df_vinaza <- read_excel("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/csv a cargar/Vinaza.xlsx")
  df_vinaza <- subset(df_vinaza, df_vinaza$NOME_PRODUCTO == "VINAZA DESPACHADA")
  a <- as.data.frame(subset(df_vinaza, df_vinaza$HACIENDA == hacienda & df_vinaza$SUERTE == suerte))
  
  if (nrow(a) == 0){
    valor_v <- 0
  }else{
    valor_v <- a$DOSIS[1] / 1000
  }
  
  return(valor_v)
}

# -------------------------------------------------------------------------
# Ciclo For----------------------------------------------------------------
# -------------------------------------------------------------------------
######Recomendaciones multiples######
vector_no_salen <- data.frame()
cont_ns <- 1
completo <- data.frame()
for (ii in (1 : nrow(df_recomendacion))) {
  hac <- df_recomendacion$Hacienda[ii]
  ste <- df_recomendacion$Suerte[ii]
  variedad <- df_recomendacion$Variedad[ii]
  tche <- df_recomendacion$`TCH Esperado`[ii]
  porc_Ncompost <- 0.8
  porc_Nvinaza <- 0.2
  compost_D <- compost(hac, ste)
  vinaza_D <- vinaza(hac, ste)

  
  shape <- RCMP(tab, hac, ste, variedad, compost_D, vinaza_D, tche, porc_Ncompost, porc_Nvinaza)
  
  if(length(shape) == 1){
    vector_no_salen[cont_ns, 1] <- hac
    vector_no_salen[cont_ns, 2] <- ste
    cont_ns <- cont_ns + 1
    next
  }else{
    fertilizantes_disponibles <- names(df_recomendacion)[which(df_recomendacion[ii, ] == "X")]
    vector_fert <- c("Naxtrom", "Nitro_Xtends", "SAM", "Nitrax", "Urea")
    ########Condicion de fertilizante###########
    ph_prom<-round(mean(shape@data$ph),2)
    #ph_prom<-8.10
    if(ph_prom <= 7.2){
      if (length(which(fertilizantes_disponibles == "Naxtrom")) != 0){
        fert <- c("Naxtrom")
        proporcion1 <- c(0, 0, 0, 0, 0)
      }else if (length(which(fertilizantes_disponibles == "Urea")) != 0){
        fert <- c("Urea")
        proporcion1 <- c(0, 0, 0, 0, 0)
      }else{
        if (length(fertilizantes_disponibles) == 1){
          fert <- c(fertilizantes_disponibles[1])
          proporcion1 <- c(0, 0, 0, 0, 0)
          proporcion1[which(vector_fert == fertilizantes_disponibles[1])] <- 100
        }else{
          dosis_menor <- 3000
          fert <- c()
          for (i in fertilizantes_disponibles) {
            a <- which(Efi$Fertilizante == i)
            dosis_op <- mean(shape@data$Dosis) / as.numeric(Efi$Eficiencia.de.absorcion[a]) 
            dosis_op <- dosis_op / as.numeric(Efi$Porcentaje.de.concentracion[a])
            if (dosis_op < dosis_menor){
              fert <- c(i)
              dosis_menor <- dosis_op
            }else{
              next
            }
          }
          proporcion1 <- c(0, 0, 0, 0, 0)
          proporcion1[which(vector_fert == fert[1])] <- 100
        }
      }
    }
    else{
      if(ph_prom > 7.2 & ph_prom <= 7.6){
        regla <- c("Nitro_Xtends", "Naxtrom")
        if (length(which(fertilizantes_disponibles == "Nitro_Xtends")) != 0){
          fert <- c("Nitro_Xtends")
          proporcion1 <- c(0, 0, 0, 0, 0)
        }else if (length(which(fertilizantes_disponibles == "Naxtrom")) != 0){
          fert <- c("Naxtrom")
          proporcion1 <- c(0, 0, 0, 0, 0)
        }else{
          if (length(fertilizantes_disponibles) == 1){
            fert <- c(fertilizantes_disponibles[1])
            proporcion1 <- c(0, 0, 0, 0, 0)
            proporcion1[which(vector_fert == fertilizantes_disponibles[1])] <- 100
          }else{
            dosis_menor <- 3000
            fert <- c()
            for (i in fertilizantes_disponibles) {
              a <- which(Efi$Fertilizante == i)
              dosis_op <- mean(shape@data$Dosis) / as.numeric(Efi$Eficiencia.de.absorcion[a]) 
              dosis_op <- dosis_op / as.numeric(Efi$Porcentaje.de.concentracion[a])
              if (dosis_op < dosis_menor){
                fert <- c(i)
                dosis_menor <- dosis_op
              }else{
                next
              }
            }
            proporcion1 <- c(0, 0, 0, 0, 0)
            proporcion1[which(vector_fert == fert[1])] <- 100
          }
        }
      }
      else{
        if(ph_prom > 7.6 & ph_prom <= 8.3){
          regla <- c("Nitro_Xtends", "SAM")
          paste('El PH promedio es ',ph_prom,'. Recomendamos fertilizar con Nitro extends y SAM.En proporcion 50/50')
          ambos_componentes_presentes <- all(regla %in% fertilizantes_disponibles)
          if (ambos_componentes_presentes == TRUE){
            fert <- regla
            proporcion1 <- c(0, 0, 0, 0, 0)
          }else if (length(which(fertilizantes_disponibles == "Nitro_Xtends")) != 0){
            dosis_menor <- 3000
            fert <- c()
            a<-which(Efi$Fertilizante == "Nitro_Xtends")
            fertilizantes_disponibles_1 <- fertilizantes_disponibles[-which(fertilizantes_disponibles == "Nitro_Xtends")]
            if (length(fertilizantes_disponibles_1) == 0){
              fert <- c("Nitro_Xtends")
              proporcion1 <- c(0, 100, 0, 0, 0)
            }else{
              for (i in fertilizantes_disponibles_1) {
                b <- which(Efi$Fertilizante == i)
                factor_absorcion     <- ((0.5 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.5 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
                factor_concentracion <- ((0.5 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.5 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
                dosis_op <- mean(shape@data$Dosis) / factor_absorcion
                dosis_op <- dosis_op / factor_concentracion
                if (dosis_op < dosis_menor){
                  fert <- c("Nitro_Xtends", i)
                  dosis_menor <- dosis_op
                }else{
                  next
                }
              }
              proporcion1 <- c(0, 0, 0, 0, 0)
              for (j in fert) {
                if (length(which(vector_fert == j)) != 0){
                  proporcion1[which(vector_fert == j)] <- 50
                }else{
                  next
                }
              }
            }
            
          }else if (length(which(fertilizantes_disponibles == "SAM")) != 0){
            dosis_menor <- 3000
            fert <- c()
            a<-which(Efi$Fertilizante == "SAM")
            fertilizantes_disponibles_1 <- fertilizantes_disponibles[-which(fertilizantes_disponibles == "SAM")]
            if (length(fertilizantes_disponibles_1) == 0){
              fert <- c("SAM")
              proporcion1 <- c(0, 0, 100, 0, 0)
            }else{
              for (i in fertilizantes_disponibles_1) {
                b <- which(Efi$Fertilizante == i)
                factor_absorcion     <- ((0.5 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.5 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
                factor_concentracion <- ((0.5 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.5 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
                dosis_op <- mean(shape@data$Dosis) / factor_absorcion
                dosis_op <- dosis_op / factor_concentracion
                if (dosis_op < dosis_menor){
                  fert <- c("SAM", i)
                  dosis_menor <- dosis_op
                }else{
                  next
                }
              }
              proporcion1 <- c(0, 0, 0, 0, 0)
              for (j in fert) {
                if (length(which(vector_fert == j)) != 0){
                  proporcion1[which(vector_fert == j)] <- 50
                }else{
                  next
                }
              }
            }
            
          }else{
            dosis_menor <- 3000
            fert <- c()
            if (length(fertilizantes_disponibles) != 1){
              combinaciones <- expand.grid(fertilizantes_disponibles, fertilizantes_disponibles)
              combinaciones_unicas <- subset(combinaciones, Var1 != Var2)
              for (i in (1 : nrow(combinaciones_unicas))) {
                b <- which(Efi$Fertilizante == as.character(combinaciones_unicas[i, 1]))
                a<-which(Efi$Fertilizante == as.character(combinaciones_unicas[i, 2]))
                factor_absorcion     <- ((0.5 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.5 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
                factor_concentracion <- ((0.5 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.5 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
                dosis_op <- mean(shape@data$Dosis) / factor_absorcion
                dosis_op <- dosis_op / factor_concentracion
                if (dosis_op < dosis_menor){
                  fert <- c(as.character(combinaciones_unicas[i, 1]), as.character(combinaciones_unicas[i, 2]))
                  dosis_menor <- dosis_op
                }else{
                  next
                }
              }
              proporcion1 <- c(0, 0, 0, 0, 0)
              for (j in fert) {
                if (length(which(vector_fert == j)) != 0){
                  proporcion1[which(vector_fert == j)] <- 50
                }else{
                  next
                }
              }
            }else{
              ##a<-which(Efi$Fertilizante == as.character(fertilizantes_disponibles[1]))
              #factor_absorcion     <- as.numeric(Efi$Eficiencia.de.absorcion[a])
              #factor_concentracion <- as.numeric(Efi$Porcentaje.de.concentracion[a])
              #dosis_op <- mean(shape@data$Dosis) / factor_absorcion
              #dosis_op <- dosis_op / factor_concentracion
              fert <- c(fertilizantes_disponibles[1])
              proporcion1 <- c(0, 0, 0, 0, 0)
              proporcion1[which(vector_fert == fertilizantes_disponibles[1])] <- 100
            }
            
          }
        }else{
          regla <- c("SAM", "Nitrax")
          ambos_componentes_presentes <- all(regla %in% fertilizantes_disponibles)
          if (ambos_componentes_presentes == TRUE){
            fert <- regla
            proporcion1 <- c(0, 0, 0, 0, 0)
          }else if (length(which(fertilizantes_disponibles == "SAM")) != 0){
            dosis_menor <- 3000
            fert <- c()
            a<-which(Efi$Fertilizante == "SAM")
            fertilizantes_disponibles_1 <- fertilizantes_disponibles[-which(fertilizantes_disponibles == "SAM")]
            if (length(fertilizantes_disponibles_1)==0){
              fert=c('SAM')
              proporcion1<- c(0, 0, 100, 0, 0)
              
            }else{
              for (i in fertilizantes_disponibles_1) {
                b <- which(Efi$Fertilizante == i)
                factor_absorcion     <- ((0.6 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.4 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
                factor_concentracion <- ((0.6 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.4 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
                dosis_op <- mean(shape@data$Dosis) / factor_absorcion
                dosis_op <- dosis_op / factor_concentracion
                if (dosis_op < dosis_menor){
                  fert <- c("SAM", i)
                  dosis_menor <- dosis_op
                }else{
                  next
                }
              }
              proporcion1<- c(0, 0, 60, 0, 0)
              fert_e <- fert[-which(fert == "SAM")]
              proporcion1[which(vector_fert == fert_e[1])] <- 40
              
              
            }
                        
          }else if (length(which(fertilizantes_disponibles == "Nitrax")) != 0){
            dosis_menor <- 3000
            fert <- c()
            a<-which(Efi$Fertilizante == "Nitrax")
            fertilizantes_disponibles_1 <- fertilizantes_disponibles[-which(fertilizantes_disponibles == "Nitrax")]
            for (i in fertilizantes_disponibles_1) {
              b <- which(Efi$Fertilizante == i)
              factor_absorcion     <- ((0.4 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.6 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
              factor_concentracion <- ((0.4 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.6 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
              dosis_op <- mean(shape@data$Dosis) / factor_absorcion
              dosis_op <- dosis_op / factor_concentracion
              if (dosis_op < dosis_menor){
                fert <- c("Nitrax", i)
                dosis_menor <- dosis_op
              }else{
                next
              }
            }
            proporcion1 <- c(0, 0, 0, 40, 0)
            fert_e <- fert[-which(fert == "Nitrax")]
            proporcion1[which(vector_fert == fert_e[1])] <- 60
          }else{
            dosis_menor <- 3000
            fert <- c()
            if (length(fertilizantes_disponibles) == 1){
              fert <- fertilizantes_disponibles
              proporcion1 <- c(0, 0, 0, 0, 0)
              proporcion1[which(vector_fert == fertilizantes_disponibles[1])] <- 100
            }else{
              combinaciones <- expand.grid(fertilizantes_disponibles, fertilizantes_disponibles)
              combinaciones_unicas <- subset(combinaciones, Var1 != Var2)
              for (i in (1 : nrow(combinaciones_unicas))) {
                b <- which(Efi$Fertilizante == as.character(combinaciones_unicas[i, 1]))
                a<-which(Efi$Fertilizante == as.character(combinaciones_unicas[i, 2]))
                factor_absorcion     <- ((0.6 / as.numeric(Efi$Eficiencia.de.absorcion[a])) + (0.4 / as.numeric(Efi$Eficiencia.de.absorcion[b])))
                factor_concentracion <- ((0.6 / as.numeric(Efi$Porcentaje.de.concentracion[a])) + (0.4 / as.numeric(Efi$Porcentaje.de.concentracion[b])))
                dosis_op <- mean(shape@data$Dosis) / factor_absorcion
                dosis_op <- dosis_op / factor_concentracion
                if (dosis_op < dosis_menor){
                  fert <- c(as.character(combinaciones_unicas[i, 1]), as.character(combinaciones_unicas[i, 2]))
                  dosis_menor <- dosis_op
                }else{
                  next
                }
              }
              proporcion1 <- c(0, 0, 0, 0, 0)
              proporcion1[which(vector_fert == fert[1])] <- 60
              proporcion1[which(vector_fert == fert[2])] <- 40
            }
            
          }#######
        }
      }
    }
    
    #####Recomendacion tabla######
    area_shape <- round((sum(shape@data$area)) / 10000, 2)
    if (df_recomendacion$`Porcentaje aplicaion 1`[ii] == 100){
      tabla1 <- recomendation(hac, ste, Naxtrom = proporcion1[1], Nitro_Xtends = proporcion1[2], SAM = proporcion1[3], Nitrax = proporcion1[4], Urea = proporcion1[5], fert = fert, shape, Efi, area_shape, as.numeric(df_recomendacion$`Area a aplicar`[ii]))
      tabla1$Fraccion <- 1
    }else{
      tab_prop <- as.data.frame(rbind(proporcion1, proporcion1))
      rownames(tab_prop) <- NULL
      names(tab_prop)<-c("Naxtrom", "Nitro_Xtends", "SAM", "Nitrax", "Urea")
      tab_prop <- tab_prop / 100
      p <- df_recomendacion$`Porcentaje aplicaion 1`[ii] / 100
      shape1 <- shape@data
      tabla1 <- recomendation_f(hac, ste, tab_prop, fert = fert, fert1 = fert, shape1, Efi, area_shape, as.numeric(df_recomendacion$`Area a aplicar`[ii]), p)
    }
    
    dbr<-data.frame(
      "Hacienda" = hac,
      "Suerte" = ste,
      "Fecha" = rep(Sys.time(), nrow(tabla1))
    )
    tabla1 <- cbind(dbr,tabla1)
    n <- nrow(tabla1)
    
    ###Condicion si hay que corregir dosis
    if(sum(df_unid_correg$Unidades) != 0){
      if (nrow(tabla1) == 1){
        factor <- tabla1$Unidades[1] / tabla1$`Kg/Ha`[1]
        area_1 <- tabla1$`Kg totales`[1] / tabla1$`Kg/Ha`[1]
        tabla1$Unidades[1] <- tabla1$Unidades[1] + df_unid_correg$Unidades[ii]
        tabla1$`Kg/Ha`[1] <- tabla1$Unidades[1] / factor
        tabla1$`Kg totales`[1] <- round(tabla1$`Kg/Ha`[1] * area_1, 2)
        tabla1$Bultos[1] <- round(tabla1$`Kg totales`[1] / 50, 2)
      }else{
        if(nrow(tabla1) == 2){
          area_1 <- tabla1$`Kg totales`[1] / tabla1$`Kg/Ha`[1]
          prop <- tabla1$Unidades[1] / sum(tabla1$Unidades)
          ####Fraccion 1
          factor1 <- tabla1$Unidades[1] / tabla1$`Kg/Ha`[1]
          tabla1$Unidades[1] <- tabla1$Unidades[1] + (df_unid_correg$Unidades[ii] * prop)
          tabla1$`Kg/Ha`[1] <- tabla1$Unidades[1] / factor1
          tabla1$`Kg totales`[1] <- round(tabla1$`Kg/Ha`[1] * area_1, 2)
          tabla1$Bultos[1] <- round(tabla1$`Kg totales`[1] / 50, 2)
          ####fraccion 2
          factor2 <- tabla1$Unidades[2] / tabla1$`Kg/Ha`[2]
          tabla1$Unidades[2] <- tabla1$Unidades[2] + (df_unid_correg$Unidades[ii] * abs(1-prop))
          tabla1$`Kg/Ha`[2] <- tabla1$Unidades[2] / factor2
          tabla1$`Kg totales`[2] <- round(tabla1$`Kg/Ha`[2] * area_1, 2)
          tabla1$Bultos[2] <- round(tabla1$`Kg totales`[2] / 50, 2)
        }else{
          area_1 <- tabla1$`Kg totales`[1] / tabla1$`Kg/Ha`[1]
          ####Fraccion 1
          prop <- tabla1$Unidades[1] / sum(tabla1$Unidades[c(1,2)])
          ####Producto 2
          unidades_c <- df_unid_correg$Unidades[ii] * (df_recomendacion$`Porcentaje aplicaion 1`[ii] / 100)
          factor1 <- tabla1$Unidades[1] / tabla1$`Kg/Ha`[1]
          tabla1$Unidades[1] <- tabla1$Unidades[1] + (unidades_c * prop)
          tabla1$`Kg/Ha`[1] <- tabla1$Unidades[1] / factor1
          tabla1$`Kg totales`[1] <- round(tabla1$`Kg/Ha`[1] * area_1, 2)
          tabla1$Bultos[1] <- round(tabla1$`Kg totales`[1] / 50, 2)
          ####Producto 1
          factor2 <- tabla1$Unidades[2] / tabla1$`Kg/Ha`[2]
          tabla1$Unidades[2] <- tabla1$Unidades[2] + (unidades_c * abs(1-prop))
          tabla1$`Kg/Ha`[2] <- tabla1$Unidades[2] / factor2
          tabla1$`Kg totales`[2] <- round(tabla1$`Kg/Ha`[2] * area_1, 2)
          tabla1$Bultos[2] <- round(tabla1$`Kg totales`[2] / 50, 2)
          
          ####fraccion 2
          prop1 <- tabla1$Unidades[3] / sum(tabla1$Unidades[c(3,4)])
          ####Producto 2
          unidades_c1 <- df_unid_correg$Unidades[ii] - unidades_c
          factor3 <- tabla1$Unidades[3] / tabla1$`Kg/Ha`[3]
          tabla1$Unidades[3] <- tabla1$Unidades[3] + (unidades_c1 * prop1)
          tabla1$`Kg/Ha`[3] <- tabla1$Unidades[3] / factor3
          tabla1$`Kg totales`[3] <- round(tabla1$`Kg/Ha`[3] * area_1, 2)
          tabla1$Bultos[3] <- round(tabla1$`Kg totales`[3] / 50, 2)
          ####Producto 1
          factor4 <- tabla1$Unidades[4] / tabla1$`Kg/Ha`[4]
          tabla1$Unidades[4] <- tabla1$Unidades[4] + (unidades_c1 * abs(1-prop1))
          tabla1$`Kg/Ha`[4] <- tabla1$Unidades[4] / factor4
          tabla1$`Kg totales`[4] <- round(tabla1$`Kg/Ha`[4] * area_1, 2)
          tabla1$Bultos[4] <- round(tabla1$`Kg totales`[4] / 50, 2)
        }
      }
    }else{
      tabla1 <- tabla1
    }
    
    df_repetido <- bind_rows(replicate(n - 1, df_recomendacion[ii, ] , simplify = FALSE), df_recomendacion[ii, ])
    df_repetido <- cbind(as.data.frame(df_repetido), tabla1)
    completo <- rbind(completo, df_repetido)
    ########################Desacarga_Recomendacion#################################
    ruta_completa_r <- paste0(ruth_e, "/" ,paste0(hac,ste,"_recomendacion.xlsx"))
    
    # Crea un libro de Excel
    wb <- createWorkbook()
    
    # Agrega una hoja al libro
    addWorksheet(wb, "Hoja1")
    
    # Escribe los datos en la hoja creada
    writeData(wb, "Hoja1", tabla1)
    
    # Guarda el archivo Excel en la ruta especificada
    saveWorkbook(wb, file = ruta_completa_r)
    
    #####Distrib tolvas######
    dir.create(paste0(ruth_s, "/" , hac, ste))
    ruth_s2 <- paste0(ruth_s, "/" , hac, ste)
    nu_frac <- levels(as.factor(tabla1$Fraccion))
    if (length(nu_frac) == 1){
      tolvas <- Distrib_tolvas(tabla1, hac, ste, area_shape, df_recomendacion$`Area a aplicar`[ii])
      if ((nrow(tolvas) == 2) & (sum(tolvas$`Kg/Ha-Real`) <= 150) & !is.na(tolvas$'TOLVA 1'[1])){
        nombre_prod <- tolvas$'TOLVA 1'[1]
        nombre_prod1 <- tolvas$'TOLVA 2'[2]
        tolvas$'TOLVA 1'[1] <- NA
        tolvas$'TOLVA 2'[2] <- NA
        tolvas$'TOLVA 2'[1] <- nombre_prod
        tolvas$'TOLVA 3'[2] <- nombre_prod1
        tolvas$'TOLVA 3'[1] <- NA
      }else{
        tolvas <- tolvas
      }
      aplicacion <- shape_verion(shape, tolvas)
      
      ###Desacragas
      writeOGR(aplicacion, dsn = ruth_s2, layer = paste0(hac,ste,"_U"), driver = "ESRI Shapefile")
      ruta_completa <- paste0(ruth_e, "/" ,paste0(hac,ste,"_U_tolvas.xlsx"))
      
      # Crea un libro de Excel
      wb <- createWorkbook()
      
      # Agrega una hoja al libro
      addWorksheet(wb, "Hoja1")
      
      # Escribe los datos en la hoja creada
      writeData(wb, "Hoja1", tolvas)
      
      # Guarda el archivo Excel en la ruta especificada
      saveWorkbook(wb, file = ruta_completa)
    }else{
      ##########################Fraccion 1 #########################################
      fraccion_1 <- subset(tabla1, tabla1$Fraccion == 1)
      tolvas_1 <- Distrib_tolvas(fraccion_1, hac, ste, area_shape, df_recomendacion$`Area a aplicar`[ii])
      if ((nrow(tolvas_1) == 2) & (sum(tolvas_1$`Kg/Ha-Real`) <= 150) & !is.na(tolvas_1$'TOLVA 1'[1])){
        nombre_prod <- tolvas_1$'TOLVA 1'[1]
        nombre_prod1 <- tolvas_1$'TOLVA 2'[2]
        tolvas_1$'TOLVA 1'[1] <- NA
        tolvas_1$'TOLVA 2'[2] <- NA
        tolvas_1$'TOLVA 2'[1] <- nombre_prod
        tolvas_1$'TOLVA 3'[2] <- nombre_prod1
        tolvas_1$'TOLVA 3'[1] <- NA
      }else{
        tolvas_1 <- tolvas_1
      }
      aplicacion_1 <- shape_verion(shape, tolvas_1)
      ###Desacragas
      writeOGR(aplicacion_1, dsn = ruth_s2, layer = paste0(hac,ste,"_F1"), driver = "ESRI Shapefile")
      ruta_completa_1 <- paste0(ruth_e, "/" ,paste0(hac,ste,"_F1_tolvas.xlsx"))
      
      # Crea un libro de Excel
      wb <- createWorkbook()
      
      # Agrega una hoja al libro
      addWorksheet(wb, "Hoja1")
      
      # Escribe los datos en la hoja creada
      writeData(wb, "Hoja1", tolvas_1)
      
      # Guarda el archivo Excel en la ruta especificada
      saveWorkbook(wb, file = ruta_completa_1)
      
      ##########################Fraccion 2 #########################################
      
      fraccion_2 <- subset(tabla1, tabla1$Fraccion == 2)
      tolvas_2 <- Distrib_tolvas(fraccion_2, hac, ste, area_shape, df_recomendacion$`Area a aplicar`[ii])
      if ((nrow(tolvas_2) == 2) & (sum(tolvas_2$`Kg/Ha-Real`) <= 150) & !is.na(tolvas_2$'TOLVA 1'[1])){
        nombre_prod <- tolvas_2$'TOLVA 1'[1]
        nombre_prod1 <- tolvas_2$'TOLVA 2'[2]
        tolvas_2$'TOLVA 1'[1] <- NA
        tolvas_2$'TOLVA 2'[2] <- NA
        tolvas_2$'TOLVA 2'[1] <- nombre_prod
        tolvas_2$'TOLVA 3'[2] <- nombre_prod1
        tolvas_2$'TOLVA 3'[1] <- NA
      }else{
        tolvas_2 <- tolvas_2
      }
      aplicacion_2 <- shape_verion(shape, tolvas_2)
      
      ###Desacragas
      writeOGR(aplicacion_2, dsn = ruth_s2, layer = paste0(hac,ste,"_F2"), driver = "ESRI Shapefile")
      ruta_completa_2 <- paste0(ruth_e, "/" ,paste0(hac,ste,"_F2_tolvas.xlsx"))
      
      # Crea un libro de Excel
      wb <- createWorkbook()
      
      # Agrega una hoja al libro
      addWorksheet(wb, "Hoja1")
      
      # Escribe los datos en la hoja creada
      writeData(wb, "Hoja1", tolvas_2)
      
      # Guarda el archivo Excel en la ruta especificada
      saveWorkbook(wb, file = ruta_completa_2)
    }
  }
  
}

########################Desacarga_Recomendacion_final#################################
completo$TCH_Maximo <- 0
BD_hist <- BD_hisotrica()
for (i in (1 : nrow(completo))) {
  completo$TCH_Maximo[i] <- TCHmax(completo$Hacienda[i], completo$Suerte[i], BD_hist)
}

columnas <- colnames(completo)

columnas <- append(columnas, "TCH_Maximo", after = 5)

columnas <- columnas[1:24]

completo <- completo[, columnas]

ruta_completa_rc <- paste0("C:/Users/sacorreac/OneDrive - Sector Agro/AP/6. FERTILIZACION TV/Salidas/", "completo_recomendacion.xlsx")#C:/Users/dfperdomo/Downloads/Fertilizacion/Descargas/

# Crea un libro de Excel
wb <- createWorkbook()

# Agrega una hoja al libro
addWorksheet(wb, "Hoja1")

# Escribe los datos en la hoja creada
writeData(wb, "Hoja1", completo)

# Guarda el archivo Excel en la ruta especificada
saveWorkbook(wb, file = ruta_completa_rc)

if(nrow(vector_no_salen) != 0){
  names(vector_no_salen) <- c("Hacienda", "Suerte")
}else{
  vector_no_salen <- data.frame()
}


