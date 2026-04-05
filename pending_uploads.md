# TikTok Upload Queue — Pendente (SDK bug bloqueado)

> Actualizado: 2026-04-05
> Status: A aguardar correcção do local-video-sdk.js do TikTok Studio

---

## Batch 5

### charconv_ubi.mp4
**Descrição:**
Peter thinks UBI sounds amazing. Stewie has thoughts. 💸 Who's right?

#ubi #universalbasicincome #economics #money #debate #aigenerated #funny

---

### charconv_quietquitting.mp4
**Descrição:**
Peter discovered quiet quitting. Stewie is not impressed. 🤫

#quietquitting #work #hustle #corporate #debate #aigenerated #funny

---

### charconv_sidehustles.mp4
**Descrição:**
Peter wants to start a side hustle. Stewie explains passive income is a myth. 💀

#sidehustle #passiveincome #money #finance #debate #aigenerated #funny

---

### charconv_healthcare.mp4
**Descrição:**
Peter compares US vs European healthcare. This gets heated fast. 🏥

#healthcare #universalhealthcare #usa #europe #debate #aigenerated #funny

---

## Batch 6 (prontos — 2026-04-05)

### charconv_cryptobubble.mp4
**Descrição:**
Peter bought Bitcoin. Stewie explains why gold has been around for 5000 years. 📉

#crypto #bitcoin #gold #investing #debate #aigenerated #funny

---

### charconv_wfh.mp4
**Descrição:**
Peter wants to work from home forever. Stewie wants the office back. 🏠

#wfh #workfromhome #remotework #office #debate #aigenerated #funny

---

### charconv_college.mp4
**Descrição:**
Peter asks if college is still worth it. Stewie has a spreadsheet. 🎓

#college #university #degree #student #debt #debate #aigenerated #funny

---

### charconv_socialmedia.mp4
**Descrição:**
Peter lets Meg use TikTok all day. Stewie pulls up the research. 📱

#socialmedia #mentalhealth #teens #tiktok #debate #aigenerated #funny

---

## Batch 7 (prontos — 2026-04-05)

### charconv_adhd.mp4
**Descrição:**
Peter got diagnosed with ADHD. Stewie looks at the data. 🧠

#adhd #mentalhealth #overdiagnosis #medication #debate #aigenerated #funny

---

### charconv_minwage.mp4
**Descrição:**
Peter thinks minimum wage should be $25. Stewie has a spreadsheet. 💵

#minimumwage #livingwage #economics #work #debate #aigenerated #funny

---

## Batch 8 (prontos — 2026-04-05)

### charconv_immig_econ.mp4
**Descrição:**
Peter thinks immigration is just good for the economy. Stewie has the numbers. 📊

#immigration #economics #debate #aigenerated #funny

---

### charconv_wlb.mp4
**Descrição:**
Peter wants work-life balance. Stewie wants him to stop being lazy. 😤

#worklifebalance #hustle #work #productivity #debate #aigenerated #funny

---

### charconv_censorship.mp4
**Descrição:**
Peter thinks social media censorship protects democracy. Stewie disagrees. 🤐

#censorship #freespeech #socialmedia #debate #aigenerated #funny

---

## Notas
- SDK bug: RangeError em local-video-sdk.7c7a7018.js — afecta TODOS os vídeos
- Testado com: vídeo 450KB gerado por ffmpeg (cor sólida), vídeos originais (70-83MB)
- Tentativas de fix: faststart re-encode → sem efeito
- Resolução: aguardar que TikTok actualize o SDK
- Monitor: cron cada 2h → ~/mind/logs/tiktok_sdk.log
- Verificar: https://www.tiktok.com/tiktokstudio/upload a cada sessão
