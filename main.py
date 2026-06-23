from ipaddress import IPv4Address
from fastapi import FastAPI, Request
from pydantic import BaseModel, AnyHttpUrl, IPvAnyAddress, ValidationError
import json
import os
import requests
import fastapi.responses
from fastapi.responses import HTMLResponse
import fastapi.templating
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import socket
import copy

app = FastAPI()

base_path = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory = os.path.join(base_path, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse(request=request,name="index.html",context={})
    except Exception as e:
        return HTMLResponse(content=f"Failed to load the template: {e}", status_code=500)
      
#Pfad für Grafana JSON Dateien hinterlegen
JsonPathDashboard = os.path.join(base_path, "monitoring", "grafana", "dashboards")
if not os.path.exists(JsonPathDashboard):
     os.makedirs(JsonPathDashboard)

#Pfad für Prometheus JSON Dateien
JsonPathPrometheus = os.path.join(base_path, "monitoring", "prometheus", "targets")
if not os.path.exists(JsonPathPrometheus):
     os.makedirs(JsonPathPrometheus)

class IpModel(BaseModel):
        ip: IPv4Address
class Website(BaseModel):
        url: AnyHttpUrl
class Swebsite(BaseModel):
        Surl: AnyHttpUrl

json_body_DB = {
  "id": None,
  "uid": None,
  "title": f"Ping",
  "timezone": "browser",
  "schemaVersion": 38,
  "version": 1,
  "refresh": "5s",
  "time": {
    "from": "now-5m",
    "to": "now"
  },
  "panels": [
    {
      "id": 1,
      "type": "timeseries",
      "title": f"Ping",
      "gridPos": {
        "x": 0,
        "y": 0,
        "h": 8,
        "w": 12
      },
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "lineWidth": 1,
            "fillOpacity": 0,
            "gradientMode": "none",
            "spanNulls": False,
            "insertNulls": False,
            "showPoints": "auto",
            "pointSize": 5,
            "stacking": {
              "mode": "none",
              "group": "A"
            }
          },
          "color": {
            "mode": "palette-classic"
          },
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "options": {
        "tooltip": {
          "mode": "single",
          "sort": "none"
        },
        "legend": {
          "showLegend": True,
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "targets": [
        {
          "refId": "A",
          "expr": "probe_icmp_duration_seconds{job='blackbox_icmp'}",
          "range": True,
          "datasource": {
            "type": "prometheus"
          }
         }
      ]
    }
  ]
}

@app.post("/get_IP")
async def get_IP(data:Website):
  domainUrl = str(data.url).strip().replace("http://","").replace("https://","").replace("/","")
  try:
     Website_IP = socket.gethostbyname(domainUrl)
     return {"ip": Website_IP}
        
  except socket.gaierror:
     return {"error": "Hostname could not be resolved."}

@app.get("/scrape_jobs/")
async def get_scrape_jobs():
     try:
          scrape_jobs = [
              dateiname.replace(".json", "")
              for dateiname in os.listdir(JsonPathDashboard)
              if dateiname.endswith(".json")
          ]
          
          return {"jobs": scrape_jobs}
     except Exception as e:
          return {"error": f"An Error occured: {str(e)}"}

@app.post("/push_icmp/") # 127.0.0.1:8000/push_icmp/
async def push_ICMP(data: IpModel):
    #IP Adresse in String umwandeln
    ip_str = str(data.ip)
    json_body_ICMP = copy.deepcopy(json_body_DB)
    json_body_ICMP['title'] = f"Ping {ip_str}"
    json_body_ICMP['panels'][0]['title'] = f"Ping {ip_str}"
    Json_Name_ICMP = f"icmp_{ip_str.replace('.','_')}.json"
    JsonPathFull_ICMP = os.path.join(JsonPathDashboard, Json_Name_ICMP)

    try:
        with open(JsonPathFull_ICMP, "w", encoding="utf-8") as f:
                json.dump(json_body_ICMP, f, indent=4)
    except Exception as e:
          return{"status:": "Failed to create JSON!", "details:": str(e)}
    
    prom_target = [
         {
              "targets": [ip_str],
              "labels": {
                   "instance": ip_str,
                   "module": "icmp"
              }
         }
    ]
    prom_file_name = f"icmp_{ip_str.replace('.','_')}.json"
    prom_file_path = os.path.join(JsonPathPrometheus, prom_file_name)

    with open(prom_file_path, "w", encoding="utf-8") as f:
         json.dump(prom_target, f, indent=4)
         return {"status": "Dashboard Grafana and Prometheus for icmp created!"}


@app.post("/push_http/")
async def push_http(data: Website):
    url_str = str(data.url)
    if url_str.startswith("http://"):
      json_body_url = copy.deepcopy(json_body_DB)
      json_body_url['title'] = f"http up {url_str}"
      json_body_url['panels'][0]['title'] = f"http up {url_str}"
      json_body_url['panels'][0]['targets'][0]['expr'] = "probe_http_duration_seconds{job='blackbox_http'}"
      Json_Name_URL = f"{url_str.replace('/','_').replace(':','_').replace('.','_')}.json"
      JsonPathFull_URL = os.path.join(JsonPathDashboard, Json_Name_URL)

      try:
            with open(JsonPathFull_URL, "w", encoding="utf-8") as f:
                    json.dump(json_body_url, f, indent=4)
      except Exception as e:
            return{"status:": "Failed to create JSON!", "details:": str(e)}
        
      prom_target = [
            {
                  "targets": [url_str],
                  "labels": {
                      "instance": url_str,
                      "module": "http_2xx"
                  }
            }
        ]
      prom_file_name = f"{url_str.replace('.','_').replace('/','_').replace(':','_')}.json"
      prom_file_path = os.path.join(JsonPathPrometheus, prom_file_name)

      with open(prom_file_path, "w", encoding="utf-8") as f:
            json.dump(prom_target, f, indent=4)
            return {"status": "Dashboard Grafana and Prometheus for http created!"}
    else: return {"URL doesn't match http criteria."}

@app.post("/push_https/") 
async def push_https(data: Swebsite):
    Surl_str = str(data.Surl)
    if Surl_str.startswith("https://"):
        json_body_Surl = copy.deepcopy(json_body_DB)
        json_body_Surl['title'] = f"https up {Surl_str}"
        json_body_Surl['panels'][0]['title'] = f"https up {Surl_str}"
        json_body_Surl['panels'][0]['targets'][0]['expr'] = "probe_http_duration_seconds{job='blackbox_https'}"
        Json_Name_SURL = f"{Surl_str.replace('/','_').replace(':','_').replace('.','_')}.json"
        JsonPathFull_SURL = os.path.join(JsonPathDashboard, Json_Name_SURL)

        try:
            with open(JsonPathFull_SURL, "w", encoding="utf-8") as f:
                json.dump(json_body_Surl, f, indent=4)
        except Exception as e:
            return{"status:": "Failed to create JSON!", "details:": str(e)}
    
        prom_target = [
         {
              "targets": [Surl_str],
              "labels": {
                   "instance": Surl_str,
                   "module": "https_2xx"
              }
         }
        ]
        prom_file_name = f"{Surl_str.replace('.','_').replace('/','_').replace(':','_')}.json"
        prom_file_path = os.path.join(JsonPathPrometheus, prom_file_name)

        with open(prom_file_path, "w", encoding="utf-8") as f:
         json.dump(prom_target, f, indent=4)
         return {"status": "Dashboard Grafana and Prometheus for https created!"}
    else: return {"status": "URL doesn't match https criteria!"}

@app.delete("/delete/")
async def delete(name: str):
      json_delete_name = f"{name}.json"
      file_path_delete = os.path.join(JsonPathDashboard, json_delete_name)
      if os.path.exists(file_path_delete):
            try:
                  os.remove(file_path_delete)
            except Exception as e:
                  return (e)

      file_path_delete_prom = os.path.join(JsonPathPrometheus, json_delete_name)
      if os.path.exists(file_path_delete_prom):
            try:
                 os.remove(file_path_delete_prom)
            except Exception as e:
                 return (e)