# coding: UTF-8
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
import cssutils
import csv
import json
import os

# ブラウザのオプションを格納する変数をもらってきます。
options = Options()

# Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
options.set_headless(True)

# ブラウザを起動する
driver = webdriver.Chrome(chrome_options=options)

# ホスト名
hosts = "https://www.oculus.com"

# urlのリスト
lists = [
"/experiences/bundles/169606067086374/",
"/experiences/go/1792865820758773/",
"/experiences/go/970225196383135/",
"/experiences/go/1585261441509589/",
"/experiences/go/1035061809913798/"
]

if not os.path.exists("out"):
  os.makedirs("out")
csvFile = open("./out/oculus.csv", 'wt', newline = '', encoding = 'utf-8')
jsonfile = open('./out/oculus.json', 'w')
jsonArray = [] # 一番外側は配列
writer = csv.writer(csvFile)

try:
  for url in lists:
    jsonObj = {} # １ページ単位のオブジェクト
    # csvの1行に対応するオブジェクトを生成（初期化）
    csvRow = []
    # ブラウザでアクセスする
    driver.get(hosts + url)

    # time.sleep(random.uniform(1,1))
    time.sleep(1)

    # HTMLを文字コードをUTF-8に変換してから取得します。
    html = driver.page_source.encode('utf-8')

    # BeautifulSoupで扱えるようにパースします
    soup = BeautifulSoup(html, "html.parser")

    # アプリ名
    nameTag = soup.find("meta", attrs={"itemprop": "name"})
    if nameTag is None:
      # アプリ名がないってことはない。それはつまり詳細ページではないからコンティニュー
      print ("continueします。")
      continue

    name = nameTag.get("content")
    csvRow.append(name)
    jsonObj["name"] = name
    print (name)
    # json.dump({"name":name},jsonfile,indent=4)

    # 評価
    ratingValueTag = soup.find("meta", attrs={"itemprop": "ratingValue"})
    if ratingValueTag is None:
      csvRow.append("")
      
      # print ("continueします。")
      # continue
    ratingValue = ratingValueTag.get("content")
    csvRow.append(ratingValue)
    jsonObj["ratingValue"] = ratingValue
    print (ratingValue)

    # 価格
    priceTag = soup.find("meta", attrs={"itemprop": "price"})
    if priceTag is None:
      csvRow.append("")
      
      # print ("continueします。")
      # continue
    price = priceTag.get("content")
    csvRow.append(price)
    jsonObj["price"] = price
    print (price)

    # 動画のURL
    videoTags = soup.find("video", attrs={"class":"_5kcv"})
    if videoTags is None:
      csvRow.append("")
    else:
      videoURL = videoTags.get("src")
      csvRow.append(videoURL)
      jsonObj["videoURL"] = videoURL
      print (videoURL)

    # サムネイル？
    thumbnailStyle = soup.find("div", attrs={"class":"_23m8"}).get("style")
    parsedThumbnailStyle = cssutils.parseStyle(thumbnailStyle)
    background_thumb_image_str = parsedThumbnailStyle["background-image"]
    thumbUrl = background_thumb_image_str.replace('url(', '').replace(')', '')
    csvRow.append(thumbUrl)
    jsonObj["thumbUrl"] = thumbUrl
    print (thumbUrl)


    # images
    imageTags = soup.find_all("div", attrs={"class":"_5e_i"})
    background_image_str_arr = []
    for imageTag in imageTags:
      style = imageTag.get("style")
      if style is None:
        continue
      # cssutilsで扱うために文字列からオブジェクト変換
      parsedStyle = cssutils.parseStyle(style)
      # url(~~~)に変換
      background_image_str = parsedStyle["background-image"]
      url = background_image_str.replace('url(', '').replace(')', '')
      csvRow.append(url)
      background_image_str_arr.append(url)
      print (url)

    jsonObj["backgroundImages"] = background_image_str_arr

    # ジャンル
    additionalInfoTag = soup.find_all("div", attrs={"class": "_21ot"})
    genreTags = additionalInfoTag[2].find_all("span", attrs={"class":"_21oz"})
    genreArr = []
    for genreTag in genreTags:
      text = genreTag.getText()
      csvRow.append(text)
      genreArr.append(text)
      writer.writerow(csvRow)

    jsonObj["genres"] = genreArr
    jsonArray.append(jsonObj)

  json.dump({"items":jsonArray},jsonfile,indent=4)
    
finally:
  csvFile.close()

