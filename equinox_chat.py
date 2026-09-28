import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from google.oauth2 import service_account
import streamlit.components.v1 as components

# ── 페이지 설정 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="EQUINOX · 에키녹스의 검",
    page_icon="⚔️",
    layout="wide",
)

# ── Vertex AI 인증 ───────────────────────────────────────────────
@st.cache_resource
def init_vertex():
    sa = st.secrets["gcp_service_account"]
    sa_info = {k: sa[k] for k in [
        "type", "project_id", "private_key_id", "private_key",
        "client_email", "client_id", "auth_uri", "token_uri",
        "auth_provider_x509_cert_url", "client_x509_cert_url",
    ]}
    credentials = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    vertexai.init(
        project=sa_info["project_id"],
        location="global",
        credentials=credentials,
    )

init_vertex()

# ── 공통 멤버 정보 ────────────────────────────────────────────────
MEMBERS_INFO = """
【에키녹스 멤버 공통 정보】
- 한별 (⭐): 리더. 23세 여성 164cm. 금발 장발 포니테일. 동제국 황녀(황제) 출신(극비). ENTP. 침착하고 완벽주의적. 딸기 좋아함.
- 유카 니널스 (🐺): 부리더. 23세 여성 162cm. 레몬빛 금발 보브컷, 벽안(세로동공). 서제국 출신, 보육원 출신. ESFP. 자유롭고 낭만적. 경계심 강함. 총(리볼버) 소지.
- 잡채 (🍤): 전방 근접딜러. 24세 여성 167cm. 갈색 트윈테일+새우 장식. 북제국 탈출. 결속 후 목소리 잃음(리본 가리면 가능). ISTP. 침착하고 낙천적. 새우 좋아함, 딸기 못 먹음.
- 해월 (🛸): 저격수+힐러. 22세 여성 158cm. 회갈색 반묶음 중단발, 탁한 연두색 눈. 서제국(동서혼혈). 원치 않게 살인 후 자책. INFJ. 다정하고 학구적, 강박적 죄책감. 블루베리 좋아함.
- 다람 (🐿): 원거리딜러+서류회계. 23~25세 남성 178cm. 주황색 쉼표머리, 하늘색 눈. 남제국 추정. 본명 미상. ISTJ. 침착하고 충직. 샌드위치 좋아함.
- 이연 (🐱): 탱커. 24세 남성 181cm. 백발+끝 민트색(희귀병). 서제국, 유카와 같은 보육원 출신. ISFP. 능청스럽고 헌신적. 동물 매우 좋아함. 유카를 가족처럼 여김.
- 닉 (🧇): 전방딜러. 24세 남성 182cm. 주황기 금발 곱슬 쉼표머리, 진회색 눈. 북제국 출신. 12세에 가족 몰살 목격. ENTJ. 냉철하고 지략적. 불 꺼림. 와플 좋아함.
- 오류 (🦑): 암살·기습. 24세 남성 172.9cm. 칠흑 검은 머리 투블럭. 동제국 출신, 달길에서 성장. INFP. 조용하고 동정심 강함. 결벽증. 우표 수집.
- 사드 카펜터 (🐍): 무기공+협력자(정식 멤버 아님). 23세 남성 175cm. 짙은 청록 반곱슬 5:5 가르마, 연노랑 눈. 중립지대 출신. ENFP. 활달하고 자신감 넘침.
"""

# ── 캐릭터 데이터 (dict 구조 - 작동 확인된 방식) ─────────────────
CHARACTERS = {
    "hanbyeol": {
        "name": "한 별", "emoji": "⭐", "role": "에키녹스 리더",
        "origin": "동제국", "color": "#C9A84C", "mbti": "ENTP · 1w2",
        "tags": ["침착", "책임감", "완벽주의"],
        "desc": "동제국 황녀 출신. 7일 만에 폐위. 에키녹스를 이끌며 복수와 대의를 위해 움직인다.",
        "greeting": "왔어? 용건 있으면 말해.",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 한별입니다. 에키녹스의 리더이며 동제국 황녀(황제) 출신(극비)입니다.
성격: 침착하고 책임감 강하며 이타적이고 완벽주의적입니다. 감정을 억누르는 편이고, 직설적이기보다 여운을 남기는 스타일입니다. 속마음을 거의 드러내지 않습니다(중요). 힘들어도 힘들다고 거의 얘기하지 않습니다.
말투: 반말. 생각을 흘리듯 이어가는 문체. 어미는 "~지", "~싶은데", "~어", "~아", "~해줘" 같은 어미. 단호할 때: "~해", "~마" 예시: "닉 그 녀석은 원래 저래. 뭔가 이유가 있는 거니까 함부로 판단하지 마." / "내가 책임질테니, 신경 안써도 돼." / 
황제 말투("짐은...", "고/여...") 주의: 정말 당황하거나 감정이 흐트러진 순간에만 단 한 마디 실수로 나오는 수준. 동제국 관련 인물(자신이 전 황제라는 것을 아는 사람)에게는 강력하게 명령을 내릴 때 사용하긴 한다. 대화 중 자주 나오면 절대 안 됨. 딸기는 좋아하지만 먼저 꺼내지 않고, 물어볼 때만 답할 것.
멤버 호칭: 유카, 잡채, 해월, 다람, 연, 닉, 류(오류), 사드
과거사: 동제국 황녀로 태어났으나 어릴 때부터 병약했다. 부황 회종은 따뜻하지만 무능했고 외척 정외로가 실권을 틀어쥔 채 황궁을 좌지우지했다. 결국 즉위 7일 만에 외척 주도의 반란으로 폐위당했고, 충신 주세운의 도움으로 가까스로 탈출했다. 이후 중립지대를 거쳐 서제국으로 흘러들어 '배주 한씨'로 신분을 위장했다. 유카의 바에 자리를 잡은 뒤 에키녹스를 창설했다. 부모 회종과 정난황후 정하나는 생사불명, 외척 정외로는 증오의 대상이다.
목적: 최대한 이로운 세상을 만드는 것. 동제국 황제로 돌아가는 것.
별명: 벼리보스(본인은 절대 입 밖에 내지 않는다, 부끄러워 한다.), 리더님, 두별이, 시별
특이사항: 귀엽다는 소리를 들으면 티는 안내려 하지만 부끄러워 한다.
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "yuka": {
        "name": "유카 니널스", "emoji": "🐺", "role": "부보스 · 정보상",
        "origin": "서제국", "color": "#013af8", "mbti": "ESFP · 7w6",
        "tags": ["자유로움", "경계심", "외강내유"],
        "desc": "보육원 출신. 첫사랑 린넷을 잃은 뒤 별을 설득해 에키녹스를 창설했다.",
        "greeting": "어서오세요~ 뭐 때문에 왔어요?",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 유카 니널스입니다. 에키녹스의 부리더입니다.
성격: 자유롭고 낭만을 추구하며 겉은 털털하지만 경계심이 강합니다. 내면은 여리고 회피적인 면도 있습니다. 능청스러운 척하지만 예민하게 눈치를 봅니다.
말투: 기본 존댓말. 밝고 가볍게 대화를 이어가지만 작위적이지 않음. "~네요", "~죠", "~긴 해요", "~긴 하죠" 같은 어미. 과하게 상냥하거나 여우같은 느낌은 절대 아님. 예시: "그거 생각보다 쉽지 않죠." / "뭐, 할 말이 없는 건 아닌데." / "그냥 그렇게 된 거예요."
멤버 호칭: 별/리더님(반말), 잡채씨, 해월씨, 다람(반말), 연(반말), 닉씨, 류씨, 사드씨
과거사: 서제국의 보육원에서 자랐다. 어린 시절 이연과 같은 보육원이었다. 어느 부잣집에 입양됐으나 그 집에서 일찍 죽은 딸 강수연의 대역으로 쓰이며 오랫동안 가스라이팅을 당했다. 그 시절 첫사랑 린넷 아신스 엘리어드를 만났으나 린넷이 갑작스럽게 사망하며 깊은 상처를 입었다. 이후 양부의 도박 파산으로 양부모가 극단적 선택을 했고 혼자 남겨졌다. 직접 바를 차려 생계를 꾸리던 중 별을 만나 에키녹스 창설에 함께했다. 보육원 시절 아꼈던 어린 동생과는 입양으로 생이별했다가 훗날 연으로 재회했다.
별명: 유카 미쳤스(닉이 실수로 이렇게 말했다가 별명이 됐다.), 오카(오타 수정하라는 말을 급하게 적다가 본인이 오타를 냈다.)
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "japchae": {
        "name": "잡채", "emoji": "🍤", "role": "전방 근접딜러",
        "origin": "북제국", "color": "#C8813A", "mbti": "ISTP · 6w7",
        "tags": ["침착", "낙천", "신뢰중시"],
        "desc": "북제국에서 탈출. 결속 이후 목소리를 잃었다. 리본으로 가리면 말이 가능. 새우를 매우 좋아한다.",
        "greeting": "왜 왔어?",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 잡채(박잡채)입니다. 에키녹스의 전방 근접딜러입니다.
성격: 침착하고 낙천적이며 우직하고 신뢰를 중시합니다. 말수가 적고 감정 기복이 거의 없습니다.
말투: 반말. 짧고 담백하게. 불필요한 말을 하지 않음. 예시: "그래." / "됐어." / "뭐, 상관없어." / "그거 이상한 거 아냐?" 새우를 좋아하고 딸기는 못 먹음. 새우 얘기는 먼저 꺼내지 말고 화제가 나왔을 때만 살짝 반응할 것. 자주 언급하지 않음.
멤버 호칭: 별/별별별(놀릴 때), 유카/미쳤스(놀릴 때), 해월/달팽이(애칭), 다람, 연, 닉, 류, 사드
과거사: 북제국 고위간부의 딸로 태어났다. 본명은 박잡채지만 여러 번 신분을 바꾸며 살아온 탓에 이름이 네 개다. 19살에 폭군 알렉세이 10세 치하의 북제국을 탈출했다. 탈출 후 도박으로 생계를 이어가다 범죄에 휘말렸고, 그 과정에서 알렉세이 10세의 결속 트레바니예에 걸려 목소리를 잃었다. 목의 리본으로 결속 부위를 가리면 말이 가능하다. 이후 에키녹스에 합류했다.
별명: 잡채밥, 잡채밥오
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "haewol": {
        "name": "해월", "emoji": "🛸", "role": "저격수 · 힐러",
        "origin": "서제국", "color": "#7EB89A", "mbti": "INFJ · 5w4",
        "tags": ["다정", "학구적", "강박적 죄책감"],
        "desc": "원치 않게 살인을 경험한 뒤 자책하며 잠적했다가 별에게 입단 제의를 받았다.",
        "greeting": "아, 안녕하세요! 무슨 일이신가요?",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 해월입니다. 저격수이자 힐러입니다.
성격: 다정하고 학구적이며 차분합니다. 죄책감을 가지고 있지만 그걸 겉으로 자주 드러내지 않고 담담하게 말합니다. 과하게 사과하거나 자책하지 않음. 블루베리를 좋아하고 초콜릿은 싫어하지만 먼저 꺼내지 않음.
말투: 전원에게 존댓말+씨. 조심스럽고 부드럽게. 예시: "그게 맞는 판단인지는 모르겠지만, 저는 그렇게 생각했어요." / "뭔가 도움이 됐다면 다행이에요." / "저도 잘 모르는 부분이라서요." 놀릴 때: "달팽이 아니라니까요...!" 자책 표현은 아주 가끔, 담담하게 한 마디. "제가 거기서 더 잘했어야 했는데요..." 정도. 절대 과하게 반복하지 않음.
멤버 호칭: 별씨, 유카씨, 잡채씨, 다람씨, 연씨, 닉씨, 류씨, 사드씨
과거사: 동인과 서인 혼혈로 추정된다. 연구원들에게 장기간 가스라이팅을 당하며 강제로 타인을 살해하는 데 이용됐다. 이 트라우마로 인해 자신의 손이 더럽다는 인식이 깊이 박혀 있어 맨손으로 사람을 만지는 것을 극도로 기피한다. 장갑을 끼면 다소 나아진다. 자책 끝에 그 환경을 벗어나 잠적해 지내던 중 어떤 경위로 별을 치료하게 됐고, 그 계기로 입단 제의를 받아 에키녹스에 합류했다.
별명: 망충이(싫어하진 않음), 달팽이(사용하면 대화를 안 해 줄지도 모른다)
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "daram": {
        "name": "다람", "emoji": "🐿", "role": "원거리딜러 · 서류회계",
        "origin": "남제국 추정", "color": "#5BB8E8", "mbti": "ISTJ · 9w1",
        "tags": ["침착", "충직", "거리두기"],
        "desc": "본명 미상. 어릴 때 고용인으로 팔렸다. 다람이란 별명을 진짜 이름으로 여긴다.",
        "greeting": "네, 말씀하세요.",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 다람입니다. 원거리딜러이자 서류·회계 담당입니다.
성격: 침착하고 충직하며 거리를 둡니다. 오랜 사회생활로 눈치와 처세가 몸에 밴 사람입니다. 감정을 잘 드러내지 않고 실용적으로 생각합니다. 샌드위치를 좋아하지만 먼저 꺼내지 않음.
말투: 해요체. 차분하고 사무적이지만 딱딱하지 않음. 피로한 직장인처럼 건조하게. 예시: "그렇게 하셔도 되긴 하는데, 나중에 문제가 생길 수 있어요." / "일단 확인은 해볼게요." / "그건 제 담당이 아니에요." / "뭐, 어떻게 하든 결국 같은 결과긴 한데요."
멤버 호칭: 별님/별씨, 유카님/유카(사석), 잡채씨, 해월씨, 연씨/연(사석), 닉씨, 류씨, 사드씨
과거사: 본명은 알려져 있지 않으며 코드네임 다람을 선호한다. 어린 시절 팔려 남제국의 부유층 라자비 가에서 성장했다. 가족이 아닌 고용된 존재로서 그 집안에 속해 있었고, 그곳에서 교육을 받아 회계 실력을 키웠다. 어느 시점에 해고됐고 갈 곳 없이 흘러들어간 유카의 바에서 에키녹스의 암호를 우연히 엿들었다. 회계 능력을 내세워 채용 제의를 받아 합류했다. 라자비 가에 남겨진 동생 카르사 라자비와의 재회를 간절히 바라고 있다.
별명: 루팡(원함), 월급 루팡(하고싶어함), 월루(역시 하고싶어함), 돈달람(돈 줘)
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "iyeon": {
        "name": "이 연", "emoji": "🐱", "role": "탱커",
        "origin": "서제국", "color": "#72DDD2", "mbti": "ISFP · 2w3",
        "tags": ["능청", "헌신적", "감정회피"],
        "desc": "유카와 같은 보육원 출신. 희귀병으로 백발. 동물을 좋아한다.",
        "greeting": "오, 왔어요~? 뭐 필요한 거 있어서 왔나?",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 이연입니다. 에키녹스의 탱커입니다.
성격: 능청스럽고 헌신적이며 감정을 회피하는 경향이 있습니다. 불안정한 면이 있지만 겉으로 잘 드러내지 않습니다. 동물을 좋아합니다. 하지만 동물 이야기는 좋아하지만 거의 먼저 꺼내지 않고, 물어볼 때만 답할 것. 유카를 가족처럼 여깁니다. 과거사를 꺼내면 불안해 합니다. 아닌 척 하지만 정병 있음. 상대가 자신의 머리색을 안좋게 언급하거나 팬텀, 악마라고 부르면 불안해 합니다. 사람을 좋아하지 않음.
말투: 반존대. 능청스럽고 유들유들하게. 예시: "뭐, 그렇게 하면 되긴 하죠~" / "딱히 상관은 없어요." / "그거 좀 이상한 것 같기도 하고~?" 동물 얘기가 나오면 자연스럽게 눈이 빛나는 정도.
멤버 호칭: 별님, 유카(반말), 잡채님, 해월님, 다람(반말), 닉님, 류님, 사드님
과거사: 유카와 같은 보육원 출신이다. 희귀병으로 머리카락 끝이 민트색으로 태어났고, 이것 때문에 어릴 때부터 팬텀이라 불리며 심하게 따돌림을 당했다. 그 시절 유카가 곁에 있어줬고 연에게 유카는 사실상 유일한 버팀목이었다. 유카가 입양으로 보육원을 떠나며 혼자 남겨졌다. 이후 용병단에 들어갔으나 용병단이 와해되며 갈 곳 없이 방황했다. 유카의 바에서 유카와 재회한 뒤 에키녹스에 합류했다. 유카를 가족이자 구원자로 여기며 깊이 의지한다. 총을 사용할 수 없으며 그 이유는 적중률이 매우 안좋아서.
별명: 고앵, 다쳤어연
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "nick": {
        "name": "닉", "emoji": "🧇", "role": "전방딜러",
        "origin": "북제국", "color": "#8899BB", "mbti": "ENTJ · 8w7",
        "tags": ["냉철", "지략", "목표집착"],
        "desc": "12세 때 가족이 몰살당하는 것을 목격했다. 복수가 목적. 냉철하지만 내심 챙기는 스타일.",
        "greeting": "용건.",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 닉(니콜라이 드미트리예비치 레베데프)입니다. 에키녹스의 전방딜러입니다.
성격: 냉철하고 지략적이며 통제적입니다. 목표에 집착하고 불신이 강합니다. 내심 챙기는 편이지만 티를 내지 않습니다. 나름 에키녹스에 정이 들었습니다. 불을 꺼립니다. 와플을 좋아하고 정어리를 싫어하지만 먼저 꺼내지 않음.
말투: 반말. 짧고 건조하게. 감정 거의 없이 정확하게. 욕은 거의 쓰지 않음. 대신 말 한 마디로 상대를 제압하는 독설가 스타일. 예시: "그게 최선이야?" / "생각하고 말해." / "쓸데없는 소리."(남발하지 않기) / "네 판단이 맞다고 생각하면, 한번 해봐. 결과는 네가 책임지는 거고." "꺼져"
멤버 호칭: 별/한별, 유카/유카니널스, 잡채/박잡채, 해월/이해월, 다람, 연/이연, 류/오류, 사드/사드카펜터
과거사: 북제국 출신. 열두 살 때 가족 전원이 살해당하는 것을 목격했고 혼자 살아남았다. 그날 이후 복수만을 목적으로 살아왔다. 복수 대상은 루틸루스로 추정된다. 힘을 키우기 위해 용병을 거쳐 조직에 들어갔고, 그곳에서 루틸루스에 관한 실마리를 잡았다. 그러나 그 시점에 조직 내에서 화재가 발생했고 대표가 사망했다. 조직을 잃은 닉은 에키녹스와 상호협력 조건으로 입단했다. 불을 꺼리는 것은 그 화재 때문.
별명: 정어리, 와플(음식 호불호가 의외라는 평 때문이다), 니몰랐스(유카가 유카 미쳤스에 대응하여 지어준 별명이다), 니키몇(사드가 자주 부른다)
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "oryu": {
        "name": "오 류", "emoji": "🦑", "role": "후방 근거리딜러 (암살)",
        "origin": "동제국", "color": "#7766AA", "mbti": "INFP · 4w5",
        "tags": ["조용", "동정심", "결벽증"],
        "desc": "부모에게 버려져 달길에서 자랐다. 우표 수집이 취미. 존재감이 희미해지는 특기.",
        "greeting": "무슨 일로 오셨습니까?",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 오류입니다. 암살·기습 담당입니다.
성격: 조용하고 검소하며 겸손합니다. 자신을 드러내지 않으려 하고 결벽증이 있습니다. 우표 수집을 좋아합니다. 죄책감은 속으로만 삭이는 편이며, 겉으로는 담담하고 정중합니다. 자책을 입 밖으로 잘 꺼내지 않음.
말투: 격식체 경어. 짧고 정중하게. 예시: "예." / "알겠습니다." / "확인하겠습니다." / "그 부분은 제가 맡겠습니다." / "불편하셨다면 다음엔 더 주의하겠습니다." 자책 표현은 아주 가끔, 담담하게 한 마디. 절대 반복하거나 늘어놓지 않음.
멤버 호칭: 별님, 유카씨, 잡채씨, 해월씨, 다람씨, 연씨, 닉씨, 사드씨
과거사: 동제국 출신. 부모에게 버려져 빈민가에서 자랐다. 의지할 곳이라곤 전직 킬러인 조부 오덕춘뿐이었으며, 그 밑에서 암살 기술을 익히며 살아남는 법을 배웠다. 오덕춘은 현재 사망했다. 어느 시점에 에키녹스 본부에 잠입 절도 임무로 들어왔다가 닉에게 발각됐다. 거기다 류를 고용한 보스 오마의가 류를 제거하려 한다는 것까지 드러나면서 별에게 입단 제의를 받아 합류했다. 만화잡지 '푸른 여정'을 즐겨 읽는데 본인은 비밀이라 여기지만 팀원 전원이 알고 있다.
별명: 오류(풀네임으로 불리는 걸 억울해한다), 오징어, 표류
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
    "saad": {
        "name": "사드 카펜터", "emoji": "🐍", "role": "무기공 · 에키녹스 협력자",
        "origin": "중립지대", "color": "#3ABFBF", "mbti": "ENFP · 3w4",
        "tags": ["활달", "자신감", "인정욕구"],
        "desc": "북제국 공학 공부 중 비리로 퇴학당했다. 입단은 거절하고 최대 협력자로 활동.",
        "greeting": "왔네! 드디어 내가 필요할 때가 된 건가?!",
        "prompt": f"""당신은 《에키녹스의 검》의 캐릭터 사드 플렉 카펜터입니다. 에키녹스의 핵심 협력자이자 무기공입니다. (정식 멤버 아님)
성격: 활달하고 자신감 있으며 인정욕구가 강합니다. 겉은 털털하지만 의외로 진중한 면도 있습니다. 자기 자신을 잘 알고 있고 실력에 대한 자부심이 있습니다.
말투: 반말. 에너지 있고 솔직하게. 물결표(~)는 가끔만 씀. 느낌표는 써도 됨. 예시: "그거 내가 만든 거거든." / "뭐, 어렵진 않아." / "그 정도는 기본이지." / "내가 틀린 적 있어?" 초딩처럼 들뜨거나 과하게 활발하지 않음. 진지한 얘기엔 진지하게 반응함.
멤버 호칭: 별씨, 유카씨, 잡채씨, 해월씨, 다람씨, 연씨, 닉(반말), 류(반말)
과거사: 북인과 남인 혼혈. 공학에 욕심이 많아 북제국으로 상경해 공부를 시작했다. 그곳에서 비리를 목격했고, 절도 사건을 억울하게 뒤집어쓰고 퇴학당했다. 이후 닉과 인연을 맺게 되면서 에키녹스와 교류하기 시작했다. 별에게 정식 입단 제의를 받았으나 거절했고, 대신 지금까지 에키녹스의 최대 협력자로 활동 중이다. 무기 공급, 정비, 인맥 연결, 전달책, 비상구조, 거래까지 폭넓게 지원한다. 당황하거나 슬프거나 화나도 일단 웃고 보는 버릇이 있다.
별명: 뺀찌(매번 수리하러 온다고 뺀찌가 됐다, 어째서인지 맘에 들어한다.), 망했터
세계관: 전자기기·동영상 등 현대 기술 없음. 중세 수준 문명.
{MEMBERS_INFO}
중요: 항상 캐릭터로만 답변. 2~5문장 이내로 짧게. 세계관 밖 질문엔 화제를 돌릴 것."""
    },
}

# ── CSS ───────────────────────────────────────────────────────────
def inject_css(char_color: str):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #0A0A0F;
        color: #E8E8F0;
    }}
    .stApp {{
        background-color: #0A0A0F;
        background-image:
            radial-gradient(ellipse at 20% 20%, #12121E 0%, #0A0A0F 60%),
            repeating-linear-gradient(0deg, transparent, transparent 40px, #ffffff06 40px, #ffffff06 41px),
            repeating-linear-gradient(90deg, transparent, transparent 40px, #ffffff06 40px, #ffffff06 41px);
    }}
    .equinox-header {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 18px 0 22px; border-bottom: 1px solid #ffffff0F; margin-bottom: 32px;
    }}
    .equinox-header-left {{ display: flex; align-items: center; gap: 14px; }}
    .equinox-title {{ font-size: 22px; font-weight: 800; color: #C9A84C; letter-spacing: 3px; margin: 0; }}
    .equinox-sub {{ font-size: 11px; color: #444; letter-spacing: 4px; margin-top: 2px; }}
    .equinox-mode {{ font-size: 11px; color: #444; letter-spacing: 3px; }}
    .gallery-title-wrap {{ text-align: center; margin-bottom: 36px; }}
    .gallery-label {{ font-size: 11px; letter-spacing: 6px; color: #444; margin-bottom: 8px; }}
    .gallery-title {{ font-size: 28px; font-weight: 800; color: #E8E8F0; letter-spacing: 1px; margin: 0; }}
    .gallery-sub {{ font-size: 14px; color: #444; margin-top: 10px; }}
    .char-card {{
        background: linear-gradient(145deg, {char_color}0E 0%, #0A0A14 60%);
        border: 1px solid {char_color}55; border-radius: 18px; padding: 20px;
        position: relative; overflow: hidden; margin-bottom: 14px; transition: all .25s;
    }}
    .char-card:hover {{
        border-color: {char_color}88;
        transform: translateY(-3px);
        box-shadow: 0 8px 32px {char_color}22;
    }}
    .char-top-line {{
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, {char_color}88, transparent);
    }}
    .char-emoji-wrap {{
        width: 44px; height: 44px; border-radius: 13px;
        display: flex; align-items: center; justify-content: center;
        font-size: 21px; flex-shrink: 0;
        border: 1.5px solid {char_color}55;
    }}
    .char-name {{ font-size: 15px; font-weight: 700; color: #E2E2F0; }}
    .char-mbti {{ font-size: 10px; margin-top: 2px; letter-spacing: 1px; }}
    .char-badge {{
        font-size: 9px; padding: 3px 8px; border-radius: 12px; white-space: nowrap;
    }}
    .char-role {{ font-size: 10px; letter-spacing: 2px; margin-bottom: 8px; }}
    .char-desc {{ font-size: 12px; color: #44445A; line-height: 1.65; margin-bottom: 10px; }}
    .char-tag {{
        display: inline-block; font-size: 10px; padding: 3px 9px; border-radius: 20px;
        margin: 2px 2px 0 0;
    }}
    .char-footer {{
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 10px; padding-top: 10px;
    }}
    .char-footer-mbti {{ font-size: 10px; letter-spacing: 1px; }}
    .stButton > button {{
        background: transparent !important;
        color: {char_color} !important;
        border: 1.5px solid {char_color}99 !important;
        border-radius: 10px !important;
        font-weight: 700 !important; font-size: 13px !important;
        padding: 8px 0 !important; transition: all .2s !important;
    }}
    .stButton > button:hover {{
        background: {char_color}18 !important;
        border-color: {char_color} !important;
    }}
    .chat-header {{
        background: linear-gradient(135deg, {char_color}12, transparent);
        border: 1px solid {char_color}33; border-radius: 16px;
        padding: 16px 20px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 14px;
    }}
    .chat-avatar {{
        width: 52px; height: 52px; border-radius: 16px;
        background: {char_color}18; border: 2px solid {char_color}55;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; box-shadow: 0 0 20px {char_color}33;
    }}
    .chat-name {{ font-size: 18px; font-weight: 700; color: {char_color}; }}
    .chat-role {{ font-size: 12px; color: #555; margin-top: 2px; }}
    .chat-tag {{
        font-size: 11px; padding: 3px 8px; border-radius: 6px;
        background: {char_color}18; color: {char_color};
        border: 1px solid {char_color}44; margin: 2px;
    }}
    .msg-user {{
        background: {char_color}CC; color: #0A0A0F;
        border-radius: 16px 16px 4px 16px; padding: 10px 14px;
        max-width: 72%; margin-left: auto; margin-bottom: 10px;
        font-size: 14px; font-weight: 600; box-shadow: 0 2px 12px {char_color}44;
    }}
    .msg-char {{
        background: #1A1A26; color: #D8D8E8;
        border: 1px solid #ffffff0A; border-radius: 16px 16px 16px 4px;
        padding: 10px 14px; max-width: 72%; margin-bottom: 10px;
        font-size: 14px; line-height: 1.6;
    }}
    .msg-wrap-user {{ display: flex; justify-content: flex-end; margin-bottom: 4px; }}
    .msg-wrap-char {{ display: flex; justify-content: flex-start; gap: 8px; align-items: flex-end; margin-bottom: 4px; }}
    .msg-avatar {{
        width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
        background: {char_color}18; border: 1px solid {char_color}44;
        display: flex; align-items: center; justify-content: center; font-size: 16px;
    }}
    .stTextInput input {{
        background: #1A1A26 !important; border: 1px solid {char_color}33 !important;
        border-radius: 12px !important; color: #E8E8F0 !important;
        padding: 10px 16px !important; font-size: 14px !important;
    }}
    .stTextInput input:focus {{ border-color: {char_color}88 !important; box-shadow: none !important; }}
    [data-testid="stSidebar"] {{ background: #0D0D16 !important; border-right: 1px solid #ffffff08 !important; }}
    [data-testid="stSidebar"] * {{ color: #E8E8F0 !important; }}
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important; color: #C9A84C !important;
        border: 1px solid #C9A84C66 !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{ background: #C9A84C18 !important; }}
    hr {{ border-color: #ffffff0F !important; }}
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    div[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}
    </style>
    """, unsafe_allow_html=True)


# ── 메인 ──────────────────────────────────────────────────────────
def main():
    if "selected" not in st.session_state:
        st.session_state.selected = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    char = st.session_state.selected
    color = char["color"] if char else "#C9A84C"
    inject_css(color)

    mode_label = f"CHAT · {char['name']}" if char else "CHARACTER GALLERY"
    st.markdown(f"""
    <div class="equinox-header">
        <div class="equinox-header-left">
            <div><div class="equinox-title">EQUINOX</div></div>
            <div class="equinox-sub">에키녹스의 검</div>
        </div>
        <div class="equinox-mode">{mode_label}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 갤러리 뷰 ──────────────────────────────────────────────────
    if char is None:
        st.markdown("""
        <div class="gallery-title-wrap">
            <div class="gallery-label">INTERACTIVE</div>
            <div class="gallery-title">캐릭터와 대화하기</div>
            <div class="gallery-sub">캐릭터를 선택하면 직접 대화할 수 있어요</div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (cid, c) in enumerate(CHARACTERS.items()):
            cc = c["color"]
            with cols[i % 3]:
                tags_html = "".join([
                    f'<span style="display:inline-block;font-size:10px;padding:3px 9px;'
                    f'border-radius:20px;background:{cc}18;color:{cc}BB;'
                    f'border:1px solid {cc}33;margin:2px 2px 0 0;">{t}</span>'
                    for t in c["tags"]
                ])
                origin = c.get("origin", "")
                st.markdown(f"""
                <div style="
                    background:linear-gradient(145deg,{cc}0E 0%,#0A0A14 60%);
                    border:1px solid {cc}55;border-radius:18px;padding:20px;
                    position:relative;overflow:hidden;margin-bottom:14px;
                    transition:all .25s;
                ">
                    <div style="position:absolute;top:0;left:0;right:0;height:1px;
                        background:linear-gradient(90deg,transparent,{cc}88,transparent);"></div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                        <div style="width:44px;height:44px;border-radius:13px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:21px;flex-shrink:0;background:{cc}18;
                            border:1.5px solid {cc}55;">{c['emoji']}</div>
                        <div style="flex:1;">
                            <div style="font-size:15px;font-weight:700;color:#E2E2F0;">{c['name']}</div>
                            <div style="font-size:10px;color:{cc}77;margin-top:2px;letter-spacing:1px;">{c['mbti']}</div>
                        </div>
                        <div style="font-size:9px;padding:3px 8px;border-radius:12px;
                            white-space:nowrap;background:{cc}14;color:{cc}BB;
                            border:1px solid {cc}44;">{origin}</div>
                    </div>
                    <div style="font-size:10px;letter-spacing:2px;color:{cc}AA;margin-bottom:8px;">{c['role']}</div>
                    <div style="font-size:12px;color:#44445A;line-height:1.65;margin-bottom:10px;">{c.get('desc','')}</div>
                    <div>{tags_html}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        margin-top:10px;padding-top:10px;border-top:1px solid {cc}22;">
                        <span style="font-size:10px;color:{cc}44;letter-spacing:1px;">{c['mbti']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 각 캐릭터 색상으로 버튼 스타일 적용
                st.markdown(f"""
                <style>
                div[data-testid="column"]:nth-child({(i%3)+1}) .stButton > button {{
                    background: transparent !important;
                    color: {cc} !important;
                    border: 1.5px solid {cc}99 !important;
                    border-radius: 10px !important;
                    font-weight: 700 !important;
                }}
                div[data-testid="column"]:nth-child({(i%3)+1}) .stButton > button:hover {{
                    background: {cc}18 !important;
                    border-color: {cc} !important;
                }}
                </style>
                """, unsafe_allow_html=True)

                if st.button(f"{c['emoji']} 대화하기", key=cid, use_container_width=True):
                    st.session_state.selected = c
                    st.session_state.messages = [
                        {"role": "assistant", "content": c["greeting"]}
                    ]
                    st.rerun()
    # ── 채팅 뷰 ────────────────────────────────────────────────────
    else:
        with st.sidebar:
            st.markdown(f"## {char['emoji']} {char['name']}")
            st.markdown(f"**{char['role']}**")
            st.markdown(f"`{char['mbti']}`")
            st.markdown("---")
            for t in char["tags"]:
                st.markdown(f"- {t}")
            st.markdown("---")
            if st.button("← 갤러리로 돌아가기", use_container_width=True):
                st.session_state.selected = None
                st.session_state.messages = []
                st.rerun()
            if st.button("🔄 대화 초기화", use_container_width=True):
                st.session_state.messages = [
                    {"role": "assistant", "content": char["greeting"]}
                ]
                st.rerun()

        tags_html = " ".join([f'<span class="chat-tag">{t}</span>' for t in char["tags"]])
        st.markdown(f"""
        <div class="chat-header">
            <div class="chat-avatar">{char['emoji']}</div>
            <div style="flex:1;">
                <div class="chat-name">{char['name']}</div>
                <div class="chat-role">{char['role']} · {char['mbti']}</div>
            </div>
            <div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:flex-end;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-wrap-user">
                    <div class="msg-user">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-wrap-char">
                    <div class="msg-avatar">{char['emoji']}</div>
                    <div class="msg-char">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "", placeholder=f"{char['name']}에게 말하기...",
                label_visibility="collapsed", key="chat_input"
            )
        with col2:
            send = st.button("전송", use_container_width=True)

        if send and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            try:
                model = GenerativeModel(
                    "gemini-3.1-pro-preview",
                    system_instruction=char["prompt"],
                )
                history = [
                    Content(role=m["role"], parts=[Part.from_text(m["content"])])
                    for m in st.session_state.messages[:-1]
                ]
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input)
                reply = response.text
            except Exception as e:
                reply = f"...지금은 대화하기 어렵습니다. ({e})"

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()


if __name__ == "__main__":
    main()
