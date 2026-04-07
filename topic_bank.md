# Charconv Topic Bank

Tópicos pré-aprovados para gerar novos vídeos. Organizados por categoria.
Formato: `--topic "TEXTO"` — copiar diretamente para o comando de geração.

## EM FILA (May 8-17 slots ocupados)
- charconv_aicoders.mp4 → May 14 ✓ (completo 6 Abr, 86MB)
- charconv_inflation.mp4 → May 15 ✓ (completo 7 Abr, 38MB)
- charconv_eu_sovereignty.mp4 → May 16 ✓ (completo 7 Abr, 36MB)
- charconv_llmintelligence.mp4 → May 17 ✓ (completo 6 Abr, ~70MB)
- charconv_socialmedia2.mp4 → May 20 ✓ (completo 7 Abr, 85MB)
- charconv_automation.mp4 → May 21 ✓ (completo 7 Abr, 90MB)
- charconv_freetrade.mp4 → May 22 ✓ (completo 7 Abr, 78MB)
- charconv_aidoctors.mp4 → May 23 (gerando 7 Abr, PID 413659)

## SLOTS OCUPADOS
- charconv_housingmarket.mp4 → May 8
- charconv_billionaires.mp4 → May 9
- charconv_socialmediaregulation.mp4 → May 10
- charconv_votingage.mp4 → May 11 ✓ (completo 6 Abr)
- charconv_gigeconomy.mp4 → May 12 ✓ (completo 6 Abr)
- charconv_maxwage.mp4 → May 13 ✓ (completo 6 Abr)

---

## TECNOLOGIA / AI

### Prontos para gerar
```
"Is AI making programmers worse? Are developers losing the ability to code without assistance?"
"Should AI-generated content be labeled? Or is that just digital segregation?"
"Can you trust AI with your money? From robo-advisors to autonomous trading."
"Is open-source AI safer than closed AI, or just less accountable?"
"Are LLMs actually intelligent, or just very sophisticated autocomplete?"
"Should AI have legal rights? What happens when an AI causes harm?"
"Will quantum computing break the internet, or is it just hype?"
```

### Já gerados
- charconv_aireplacement.mp4 (AI replacing jobs)
- charconv_ai_devs.mp4 (AI replacing junior devs)
- charconv_socialmedia.mp4

---

## ECONOMIA / TRABALHO

### Prontos para gerar
```
"Is gig economy freedom or exploitation? Uber drivers vs employees."
"Should there be a maximum wage? If there's a minimum, why not a maximum?"
"Will AI replace doctors, or just make bad doctors more dangerous?"
"Should inheritance be taxed at 100%? Is inherited wealth earned wealth?"
"Is free trade actually free? Who wins and who loses from globalization?"
"Should banks be nationalized? Are private banks a public risk?"
"Is inflation a hidden tax? Who benefits from devaluing the currency?"
"Are CEOs worth 300x the average worker salary? What the data says."
```

### Já gerados
- charconv_minwage.mp4
- charconv_ubi.mp4
- charconv_wfh.mp4
- charconv_quietquitting.mp4
- charconv_4daywk.mp4
- charconv_wlb.mp4
- charconv_sidehustles.mp4
- charconv_wagegap.mp4
- charconv_salary_data.mp4
- charconv_billionaires.mp4
- charconv_housingmarket.mp4
- charconv_automation.mp4
- charconv_freetrade.mp4
- charconv_aidoctors.mp4 (gerando)

---

## SAÚDE / SOCIEDADE

### Prontos para gerar
```
"Should junk food be taxed like cigarettes? The case for sugar taxes."
"Is mental health the new hypochondria? Are we medicalizing normal emotions?"
"Should euthanasia be legal? The right to die debate."
"Is homeschooling better than traditional schooling? Evidence vs ideology."
"Should organs be harvested automatically unless you opt out?"
"Is porn addictive? What the science actually says."
"Should voting be mandatory? Democracy works better with participation."
"Is cancel culture real, or just accountability finally working?"
```

### Já gerados
- charconv_adhd.mp4
- charconv_cancelculture.mp4
- charconv_veganism.mp4

---

## POLÍTICA / GEOPOLÍTICA

### Prontos para gerar
```
"Should countries have open borders? The economic and social case."
"Is the EU a superstate in disguise? Sovereignty vs integration."
"Is nationalism making a comeback, and is that good or bad?"
"Should politicians be paid more to reduce corruption?"
"Is democracy the best system, or just the least bad?"
"Should nuclear weapons be abolished, or do they prevent wars?"
"Is China a threat to the West, or just a competitor?"
"Should the UN be reformed or abolished?"
```

### Já gerados
- charconv_immig_econ.mp4
- charconv_censorship.mp4
- charconv_eu_army.mp4
- charconv_japan_robots.mp4
- charconv_lockdown.mp4
- charconv_socialmediaregulation.mp4
- charconv_votingage.mp4

---

## AMBIENTE / ENERGIA

### Prontos para gerar
```
"Is nuclear energy the only realistic path to net zero?"
"Are electric vehicles actually green? The battery problem."
"Should flying be taxed heavily to fight climate change?"
"Is climate change being used to justify authoritarianism?"
"Are lab-grown meats the future of food, or a Silicon Valley delusion?"
"Should plastic bags be banned? Does it make any difference?"
```

### Já gerados
- charconv_nuclear.mp4
- charconv_electricvehicles.mp4

---

## CULTURA / ENTRETENIMENTO

### Prontos para gerar
```
"Is streaming killing music? Artists vs platforms in the attention economy."
"Should video games be regulated like gambling? The loot box debate."
"Is social media making teenagers depressed, or are depressed teenagers using social media more?"
"Should violent video games be banned? What 30 years of research says."
"Is college worth it anymore? Tuition costs vs job market reality."
"Should sex work be legalized and regulated?"
```

### Já gerados
- charconv_college.mp4
- charconv_socialmedia.mp4
- charconv_studentloans.mp4

---

## OUTROS / MISC

### Prontos para gerar
```
"Should drugs be legal? Portugal did it. What happened?"
"Is religion good for society? The statistics might surprise you."
"Should the rich pay more taxes, or do they already pay enough?"
"Is capitalism broken, or just capitalism working as designed?"
"Should the death penalty be abolished? Arguments from both sides."
"Is privacy dead? What surveillance capitalism means for freedom."
"Are suburbs destroying the environment and mental health?"
```

### Já gerados
- charconv_drugdecrim.mp4
- charconv_cryptobubble.mp4
- charconv_rentcontrol.mp4
- charconv_nomads.mp4
- charconv_replication.mp4
- charconv_ubi_web.mp4
- charconv_healthcare.mp4
- charconv_inflation.mp4
- charconv_eu_sovereignty.mp4
- charconv_politiciansalary.mp4
- charconv_airights.mp4
- charconv_socialmedia2.mp4

---

## NOTAS DE USO

Comando base:
```bash
cd /home/osno/projects/osno-charconv
nohup python3 generate_dialogue.py \
  --topic "TEXTO DO TOPICO AQUI" \
  --engine fish \
  --output output/charconv_NOME.mp4 \
  > /tmp/charconv_NOME.log 2>&1 &
```

Depois de gerado: adicionar a `yt_upload_charconv.py` e a `osno-site/index.html`.
