import json
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Indian Trading Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SETTINGS
# ============================================================

SETTINGS_FILE = (
    Path.home()
    / ".indian_trading_dashboard.json"
)

SYMBOLS = [
    "NIFTY50",
    "BANKNIFTY",
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "KOTAKBANK.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "TATAMOTORS.NS",
]

YF_SYMBOL_MAP = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "RELIANCE.NS": "RELIANCE.NS",
    "TCS.NS": "TCS.NS",
    "INFY.NS": "INFY.NS",
    "HDFCBANK.NS": "HDFCBANK.NS",
    "ICICIBANK.NS": "ICICIBANK.NS",
    "SBIN.NS": "SBIN.NS",
    "ITC.NS": "ITC.NS",
    "LT.NS": "LT.NS",
    "BHARTIARTL.NS": "BHARTIARTL.NS",
    "KOTAKBANK.NS": "KOTAKBANK.NS",
    "AXISBANK.NS": "AXISBANK.NS",
    "MARUTI.NS": "MARUTI.NS",
    "TATAMOTORS.NS": "TATAMOTORS.NS",
}


# ============================================================
# TIMEFRAMES
# ============================================================

TIMEFRAMES = {
    "1m": {
        "interval": "1m",
        "period": "5d",
    },
    "5m": {
        "interval": "5m",
        "period": "1mo",
    },
    "15m": {
        "interval": "15m",
        "period": "1mo",
    },
    "30m": {
        "interval": "30m",
        "period": "1mo",
    },
    "1h": {
        "interval": "1h",
        "period": "3mo",
    },
    "1d": {
        "interval": "1d",
        "period": "2y",
    },
    "1wk": {
        "interval": "1wk",
        "period": "5y",
    },
}


# ============================================================
# INDICATORS
# ============================================================

INDICATORS = [
    "None",
    "SMA",
    "EMA",
    "Bollinger Bands",
    "VWAP",
    "RSI",
    "MACD",
]


DEFAULT_CHARTS = [
    {
        "symbol": "NIFTY50",
        "timeframe": "5m",
        "indicator": "SMA",
    },
    {
        "symbol": "BANKNIFTY",
        "timeframe": "5m",
        "indicator": "EMA",
    },
    {
        "symbol": "RELIANCE.NS",
        "timeframe": "15m",
        "indicator": "Bollinger Bands",
    },
    {
        "symbol": "TCS.NS",
        "timeframe": "15m",
        "indicator": "None",
    },
    {
        "symbol": "INFY.NS",
        "timeframe": "15m",
        "indicator": "VWAP",
    },
    {
        "symbol": "HDFCBANK.NS",
        "timeframe": "15m",
        "indicator": "EMA",
    },
    {
        "symbol": "ICICIBANK.NS",
        "timeframe": "15m",
        "indicator": "RSI",
    },
    {
        "symbol": "SBIN.NS",
        "timeframe": "15m",
        "indicator": "MACD",
    },
]


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_settings():

    result = {
        "chart_count": 4,
        "charts": [
            item.copy()
            for item in DEFAULT_CHARTS
        ],
    }

    try:

        if not SETTINGS_FILE.exists():
            return result

        data = json.loads(
            SETTINGS_FILE.read_text()
        )

        chart_count = data.get(
            "chart_count"
        )

        if chart_count in [
            1,
            2,
            4,
            6,
            8,
        ]:

            result["chart_count"] = (
                chart_count
            )

        saved_charts = data.get(
            "charts"
        )

        if isinstance(
            saved_charts,
            list,
        ):

            for i, item in enumerate(
                saved_charts[:8]
            ):

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                symbol = item.get(
                    "symbol"
                )

                timeframe = item.get(
                    "timeframe"
                )

                indicator = item.get(
                    "indicator",
                    "None",
                )

                if indicator not in INDICATORS:
                    indicator = "None"

                if (
                    symbol in SYMBOLS
                    and
                    timeframe in TIMEFRAMES
                ):

                    result["charts"][i] = {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "indicator": indicator,
                    }

    except Exception:
        pass

    return result


# ============================================================
# SAVE SETTINGS
# ============================================================

def save_settings():

    try:

        data = {
            "chart_count":
                st.session_state.chart_count,

            "charts":
                st.session_state.charts,
        }

        SETTINGS_FILE.write_text(
            json.dumps(
                data,
                indent=2,
            )
        )

    except Exception:
        pass


# ============================================================
# SESSION STATE
# ============================================================

if "initialized" not in st.session_state:

    saved_settings = load_settings()

    st.session_state.chart_count = (
        saved_settings["chart_count"]
    )

    st.session_state.charts = (
        saved_settings["charts"]
    )

    st.session_state.previous_prices = {}

    st.session_state.initialized = True


# ============================================================
# MARKET DATA
# ============================================================

@st.cache_data(
    ttl=15,
    show_spinner=False,
)
def get_market_dataframe(
    symbol,
    timeframe,
):

    yf_symbol = YF_SYMBOL_MAP.get(
        symbol
    )

    if yf_symbol is None:
        return pd.DataFrame()

    timeframe_settings = TIMEFRAMES.get(
        timeframe
    )

    if timeframe_settings is None:
        return pd.DataFrame()

    try:

        dataframe = yf.download(
            yf_symbol,
            period=timeframe_settings["period"],
            interval=timeframe_settings["interval"],
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return pd.DataFrame()

        if isinstance(
            dataframe.columns,
            pd.MultiIndex,
        ):

            dataframe.columns = [
                column[0]
                for column in dataframe.columns
            ]

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]

        for column in required_columns:

            if column not in dataframe.columns:
                return pd.DataFrame()

        dataframe = dataframe.dropna(
            subset=required_columns
        )

        return dataframe.tail(500)

    except Exception:

        return pd.DataFrame()


# ============================================================
# PREPARE CANDLES
# ============================================================

def prepare_candles(dataframe):

    candles = []

    if dataframe.empty:
        return candles

    for timestamp, row in dataframe.iterrows():

        try:

            timestamp = pd.Timestamp(
                timestamp
            )

            if timestamp.tzinfo is not None:

                timestamp = timestamp.tz_convert(
                    "UTC"
                )

            candles.append(
                {
                    "time": int(
                        timestamp.timestamp()
                    ),
                    "open": float(
                        row["Open"]
                    ),
                    "high": float(
                        row["High"]
                    ),
                    "low": float(
                        row["Low"]
                    ),
                    "close": float(
                        row["Close"]
                    ),
                }
            )

        except Exception:
            continue

    return candles


# ============================================================
# INDICATOR CALCULATIONS
# ============================================================

def calculate_indicators(dataframe):

    if dataframe.empty:
        return {}

    close = dataframe["Close"].astype(
        float
    )

    high = dataframe["High"].astype(
        float
    )

    low = dataframe["Low"].astype(
        float
    )

    volume = None

    if "Volume" in dataframe.columns:

        volume = dataframe[
            "Volume"
        ].astype(float)

    result = {}

    # --------------------------------------------------------
    # SMA
    # --------------------------------------------------------

    sma = close.rolling(
        window=20
    ).mean()

    result["SMA"] = sma

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    ema = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    result["EMA"] = ema

    # --------------------------------------------------------
    # Bollinger Bands
    # --------------------------------------------------------

    bb_middle = close.rolling(
        window=20
    ).mean()

    bb_std = close.rolling(
        window=20
    ).std()

    bb_upper = (
        bb_middle
        +
        2 * bb_std
    )

    bb_lower = (
        bb_middle
        -
        2 * bb_std
    )

    result["BB_MIDDLE"] = bb_middle
    result["BB_UPPER"] = bb_upper
    result["BB_LOWER"] = bb_lower

    # --------------------------------------------------------
    # VWAP
    # --------------------------------------------------------

    if volume is not None:

        typical_price = (
            high
            +
            low
            +
            close
        ) / 3

        cumulative_volume = (
            volume.cumsum()
        )

        safe_volume = (
            cumulative_volume
            .replace(
                0,
                pd.NA,
            )
        )

        vwap = (
            (
                typical_price
                * volume
            ).cumsum()
            / safe_volume
        )

        result["VWAP"] = vwap

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    delta = close.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    average_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
    ).mean()

    rs = (
        average_gain
        /
        average_loss.replace(
            0,
            pd.NA,
        )
    )

    rsi = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )

    result["RSI"] = rsi

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    ema_12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema_26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    macd = (
        ema_12
        -
        ema_26
    )

    signal = macd.ewm(
        span=9,
        adjust=False,
    ).mean()

    histogram = (
        macd
        -
        signal
    )

    result["MACD"] = macd
    result["MACD_SIGNAL"] = signal
    result["MACD_HISTOGRAM"] = histogram

    return result


# ============================================================
# CONVERT INDICATOR TO JAVASCRIPT DATA
# ============================================================

def indicator_series(
    dataframe,
    series,
):

    output = []

    if dataframe.empty:
        return output

    for timestamp, value in series.items():

        try:

            if pd.isna(value):
                continue

            timestamp = pd.Timestamp(
                timestamp
            )

            if timestamp.tzinfo is not None:

                timestamp = timestamp.tz_convert(
                    "UTC"
                )

            output.append(
                {
                    "time": int(
                        timestamp.timestamp()
                    ),
                    "value": float(
                        value
                    ),
                }
            )

        except Exception:
            continue

    return output


# ============================================================
# BUILD INDICATOR PAYLOAD
# ============================================================

def build_indicator_payload(
    dataframe,
    indicator,
):

    calculated = calculate_indicators(
        dataframe
    )

    payload = {
        "sma": [],
        "ema": [],
        "bb_middle": [],
        "bb_upper": [],
        "bb_lower": [],
        "vwap": [],
        "rsi": [],
        "macd": [],
        "macd_signal": [],
        "macd_histogram": [],
    }

    if indicator == "SMA":

        payload["sma"] = indicator_series(
            dataframe,
            calculated["SMA"],
        )

    elif indicator == "EMA":

        payload["ema"] = indicator_series(
            dataframe,
            calculated["EMA"],
        )

    elif indicator == "Bollinger Bands":

        payload["bb_middle"] = indicator_series(
            dataframe,
            calculated["BB_MIDDLE"],
        )

        payload["bb_upper"] = indicator_series(
            dataframe,
            calculated["BB_UPPER"],
        )

        payload["bb_lower"] = indicator_series(
            dataframe,
            calculated["BB_LOWER"],
        )

    elif indicator == "VWAP":

        if "VWAP" in calculated:

            payload["vwap"] = indicator_series(
                dataframe,
                calculated["VWAP"],
            )

    elif indicator == "RSI":

        payload["rsi"] = indicator_series(
            dataframe,
            calculated["RSI"],
        )

    elif indicator == "MACD":

        payload["macd"] = indicator_series(
            dataframe,
            calculated["MACD"],
        )

        payload["macd_signal"] = indicator_series(
            dataframe,
            calculated["MACD_SIGNAL"],
        )

        payload["macd_histogram"] = indicator_series(
            dataframe,
            calculated["MACD_HISTOGRAM"],
        )

    return payload


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

[data-testid="stHeader"] {
    height: 0px !important;
    min-height: 0px !important;
    background: transparent !important;
    border: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stStatusWidget"] {
    display: none !important;
}

button[kind="header"] {
    display: none !important;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background: #f3f8fd !important;
}

.block-container {

    max-width: 100% !important;

    padding-top: 3.5rem !important;

    padding-left: 1.25rem !important;

    padding-right: 1.25rem !important;

    padding-bottom: 1rem !important;
}

.title-main {

    color: #123b5d;

    font-size: 25px;

    font-weight: 800;

    line-height: 1.2;

    margin-top: 4px;
}

.title-sub {

    color: #71869a;

    font-size: 12px;

    margin-top: 5px;
}

.status-text {

    color: #1675b3;

    font-size: 12px;

    font-weight: 700;

    padding-top: 12px;
}

div[data-baseweb="select"] > div {

    background: #ffffff !important;

    border: 1px solid #b9d1e5 !important;

    border-radius: 8px !important;

    min-height: 38px !important;

    box-shadow: none !important;
}

div[data-baseweb="select"] > div:hover {

    border-color: #4da4d8 !important;
}

div[data-baseweb="select"] * {

    color: #183247 !important;
}

div[role="listbox"] {

    background: #ffffff !important;
}

div[role="option"] {

    background: #ffffff !important;

    color: #183247 !important;
}

div[role="option"]:hover {

    background: #eaf6ff !important;

    color: #0875b5 !important;
}

.chart-panel {

    background: #ffffff;

    border: 1px solid #d4e2ee;

    border-radius: 10px;

    padding: 10px;

    margin-bottom: 12px;

    box-shadow:
        0 3px 12px
        rgba(41, 86, 125, 0.08);
}

.chart-title {

    color: #123b5d;

    font-size: 14px;

    font-weight: 800;

    margin-bottom: 5px;
}

[data-testid="stIFrame"] {

    border:
        1px solid #d6e3ed !important;

    border-radius:
        7px !important;

    overflow:
        hidden !important;

    background:
        #ffffff !important;
}

.footer {

    text-align: center;

    color: #7890a4;

    font-size: 10px;

    padding: 12px 0;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# TOP SPACE
# ============================================================

st.write("")


# ============================================================
# HEADER
# ============================================================

header_left, header_middle, header_right = st.columns(
    [5, 2, 3],
    vertical_alignment="center",
)

with header_left:

    st.markdown(
        '<div class="title-main">'
        '📈 Indian Trading Terminal'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="title-sub">'
        'Multi-chart market dashboard • Yahoo Finance'
        '</div>',
        unsafe_allow_html=True,
    )


with header_middle:

    chart_count = st.selectbox(
        "Charts",
        [1, 2, 4, 6, 8],
        index=[
            1,
            2,
            4,
            6,
            8,
        ].index(
            st.session_state.chart_count
        ),
        key="number_of_charts",
    )


with header_right:

    st.markdown(
        '<div class="status-text">'
        '🟢 LOCAL MARKET DATA'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "No API key required"
    )


# ============================================================
# CHART COUNT
# ============================================================

if (
    chart_count
    !=
    st.session_state.chart_count
):

    st.session_state.chart_count = (
        chart_count
    )

    save_settings()

    st.rerun()


# ============================================================
# GRID
# ============================================================

if chart_count == 1:

    columns_count = 1

elif chart_count == 2:

    columns_count = 2

elif chart_count == 4:

    columns_count = 2

elif chart_count == 6:

    columns_count = 3

else:

    columns_count = 4


# ============================================================
# RENDER CHARTS
# ============================================================

for row_start in range(
    0,
    chart_count,
    columns_count,
):

    columns = st.columns(
        columns_count,
        gap="small",
    )

    for column_index, column in enumerate(
        columns
    ):

        chart_index = (
            row_start
            +
            column_index
        )

        if chart_index >= chart_count:
            break

        chart_state = (
            st.session_state.charts[
                chart_index
            ]
        )

        with column:

            st.markdown(
                '<div class="chart-panel">',
                unsafe_allow_html=True,
            )

            # =================================================
            # TITLE
            # =================================================

            st.markdown(
                f'<div class="chart-title">'
                f'Chart {chart_index + 1}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # =================================================
            # CONTROLS
            # =================================================

            symbol_column, timeframe_column, indicator_column = (
                st.columns(
                    [2.0, 1.0, 1.5],
                    vertical_alignment="bottom",
                )
            )

            with symbol_column:

                symbol = st.selectbox(
                    "Symbol",
                    SYMBOLS,
                    index=SYMBOLS.index(
                        chart_state["symbol"]
                    ),
                    key=(
                        "symbol_"
                        + str(chart_index)
                    ),
                )

            with timeframe_column:

                timeframe = st.selectbox(
                    "Timeframe",
                    list(
                        TIMEFRAMES.keys()
                    ),
                    index=list(
                        TIMEFRAMES.keys()
                    ).index(
                        chart_state[
                            "timeframe"
                        ]
                    ),
                    key=(
                        "timeframe_"
                        + str(chart_index)
                    ),
                )

            with indicator_column:

                indicator = st.selectbox(
                    "Indicator",
                    INDICATORS,
                    index=INDICATORS.index(
                        chart_state.get(
                            "indicator",
                            "None",
                        )
                    ),
                    key=(
                        "indicator_"
                        + str(chart_index)
                    ),
                )

            # =================================================
            # SAVE
            # =================================================

            changed = False

            if (
                chart_state["symbol"]
                !=
                symbol
            ):

                chart_state["symbol"] = symbol

                changed = True

            if (
                chart_state["timeframe"]
                !=
                timeframe
            ):

                chart_state["timeframe"] = (
                    timeframe
                )

                changed = True

            if (
                chart_state.get(
                    "indicator",
                    "None",
                )
                !=
                indicator
            ):

                chart_state["indicator"] = (
                    indicator
                )

                changed = True

            if changed:

                save_settings()

            # =================================================
            # DATA
            # =================================================

            dataframe = get_market_dataframe(
                symbol,
                timeframe,
            )

            candles = prepare_candles(
                dataframe
            )

            indicator_payload = (
                build_indicator_payload(
                    dataframe,
                    indicator,
                )
            )

            # =================================================
            # PRICE
            # =================================================

            current_price = None

            if candles:

                current_price = candles[
                    -1
                ]["close"]

            previous_price = (
                st.session_state.previous_prices.get(
                    chart_index
                )
            )

            direction = "same"

            if (
                current_price is not None
                and
                previous_price is not None
            ):

                if (
                    current_price
                    >
                    previous_price
                ):

                    direction = "up"

                elif (
                    current_price
                    <
                    previous_price
                ):

                    direction = "down"

            if current_price is None:

                price_text = "Loading..."

            else:

                price_text = (
                    f"{current_price:,.2f}"
                )

            st.session_state.previous_prices[
                chart_index
            ] = current_price

            # =================================================
            # INFO
            # =================================================

            info_left, info_middle, info_right = st.columns(
                [2, 1, 2],
                vertical_alignment="center",
            )

            with info_left:

                st.write(
                    f"**{symbol}**"
                )

            with info_middle:

                st.caption(
                    timeframe
                )

            with info_right:

                if direction == "up":

                    st.success(
                        f"▲ {price_text}",
                        icon="📈",
                    )

                elif direction == "down":

                    st.error(
                        f"▼ {price_text}",
                        icon="📉",
                    )

                else:

                    st.info(
                        f"● {price_text}",
                        icon="💰",
                    )

            # =================================================
            # CHART HTML
            # =================================================

            candles_json = json.dumps(
                candles
            )

            indicators_json = json.dumps(
                indicator_payload
            )

            chart_html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>

<style>

html,
body {{

    margin: 0;

    padding: 0;

    width: 100%;

    height: 100%;

    overflow: hidden;

    background: #ffffff;

}}

#chart {{

    width: 100%;

    height: 100%;

    background: #ffffff;

}}

</style>

</head>

<body>

<div id="chart"></div>

<script>

const candles = {candles_json};

const indicators = {indicators_json};

const container =
    document.getElementById(
        "chart"
    );

const chart =
    LightweightCharts.createChart(
        container,
        {{

            width:
                container.clientWidth,

            height:
                container.clientHeight,

            layout: {{

                background: {{
                    type: "solid",
                    color: "#ffffff"
                }},

                textColor:
                    "#506579"

            }},

            grid: {{

                vertLines: {{
                    color: "#edf3f8"
                }},

                horzLines: {{
                    color: "#edf3f8"
                }}

            }},

            rightPriceScale: {{

                borderColor:
                    "#d6e3ed",

                textColor:
                    "#506579",

                scaleMargins: {{

                    top: 0.08,

                    bottom: 0.08

                }}

            }},

            timeScale: {{

                borderColor:
                    "#d6e3ed",

                timeVisible:
                    true,

                secondsVisible:
                    false,

                rightOffset:
                    5,

                barSpacing:
                    7

            }},

            crosshair: {{

                mode:
                    LightweightCharts
                    .CrosshairMode
                    .Normal

            }}

        }}
    );


/* ==========================================================
   CANDLESTICKS
   ========================================================== */

const candleSeries =
    chart.addSeries(
        LightweightCharts
            .CandlestickSeries,
        {{

            upColor:
                "#159a85",

            downColor:
                "#e05252",

            borderUpColor:
                "#159a85",

            borderDownColor:
                "#e05252",

            wickUpColor:
                "#159a85",

            wickDownColor:
                "#e05252"

        }}
    );


if (
    candles &&
    candles.length > 0
) {{

    candleSeries.setData(
        candles
    );

}}


/* ==========================================================
   SMA
   ========================================================== */

if (
    indicators.sma &&
    indicators.sma.length > 0
) {{

    const smaSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#1976d2",

                lineWidth:
                    2,

                title:
                    "SMA 20",

                priceLineVisible:
                    false,

                lastValueVisible:
                    true

            }}
        );

    smaSeries.setData(
        indicators.sma
    );

}}


/* ==========================================================
   EMA
   ========================================================== */

if (
    indicators.ema &&
    indicators.ema.length > 0
) {{

    const emaSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#f59e0b",

                lineWidth:
                    2,

                title:
                    "EMA 20",

                priceLineVisible:
                    false,

                lastValueVisible:
                    true

            }}
        );

    emaSeries.setData(
        indicators.ema
    );

}}


/* ==========================================================
   BOLLINGER BANDS
   ========================================================== */

if (
    indicators.bb_middle &&
    indicators.bb_middle.length > 0
) {{

    const middle =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#1976d2",

                lineWidth:
                    1,

                title:
                    "BB Middle",

                priceLineVisible:
                    false

            }}
        );

    middle.setData(
        indicators.bb_middle
    );


    const upper =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#8b5cf6",

                lineWidth:
                    1,

                title:
                    "BB Upper",

                priceLineVisible:
                    false

            }}
        );

    upper.setData(
        indicators.bb_upper
    );


    const lower =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#8b5cf6",

                lineWidth:
                    1,

                title:
                    "BB Lower",

                priceLineVisible:
                    false

            }}
        );

    lower.setData(
        indicators.bb_lower
    );

}}


/* ==========================================================
   VWAP
   ========================================================== */

if (
    indicators.vwap &&
    indicators.vwap.length > 0
) {{

    const vwapSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#ef4444",

                lineWidth:
                    2,

                title:
                    "VWAP",

                priceLineVisible:
                    false,

                lastValueVisible:
                    true

            }}
        );

    vwapSeries.setData(
        indicators.vwap
    );

}}


/* ==========================================================
   RSI
   ========================================================== */

if (
    indicators.rsi &&
    indicators.rsi.length > 0
) {{

    const rsiSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#8b5cf6",

                lineWidth:
                    2,

                title:
                    "RSI 14",

                priceLineVisible:
                    false,

                lastValueVisible:
                    true

            }}
        );

    rsiSeries.setData(
        indicators.rsi
    );

}}


/* ==========================================================
   MACD
   ========================================================== */

if (
    indicators.macd &&
    indicators.macd.length > 0
) {{

    const macdSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#1976d2",

                lineWidth:
                    2,

                title:
                    "MACD",

                priceLineVisible:
                    false

            }}
        );

    macdSeries.setData(
        indicators.macd
    );


    const signalSeries =
        chart.addSeries(
            LightweightCharts
                .LineSeries,
            {{

                color:
                    "#ef4444",

                lineWidth:
                    2,

                title:
                    "Signal",

                priceLineVisible:
                    false

            }}
        );

    signalSeries.setData(
        indicators.macd_signal
    );

}}


/* ==========================================================
   FIT CONTENT
   ========================================================== */

if (
    candles &&
    candles.length > 0
) {{

    chart.timeScale()
        .fitContent();

}}


/* ==========================================================
   RESIZE
   ========================================================== */

const resizeObserver =
    new ResizeObserver(
        function(entries) {{

            if (
                !entries.length
            ) {{
                return;
            }}

            const rect =
                entries[0]
                .contentRect;

            chart.resize(
                rect.width,
                rect.height
            );

        }}
    );

resizeObserver.observe(
    container
);

</script>

</body>

</html>
"""

            st.components.v1.html(
                chart_html,
                height=350,
                scrolling=False,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'Indian Trading Terminal • '
    'Lightweight Charts • '
    'Yahoo Finance • '
    'Local Machine'
    '</div>',
    unsafe_allow_html=True,
)
