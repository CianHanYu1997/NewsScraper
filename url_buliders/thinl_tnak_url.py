from url_buliders.base import URLParameters, BaseURLBuilder


class CFRURLBuilder(BaseURLBuilder):
    """外交關係協會的URL構建器"""

    def __init__(self):
        super().__init__(URLParameters(
            base_url="https://www.cfr.org/asia/china",
            filter_params={
                "topics": "All",
                "regions": "All"
            },
            type_param_key="type",
            type_param_format="{type}"
        ))


class BrookingsURLBuilder(BaseURLBuilder):
    """布魯金斯研究所的URL構建器"""

    def __init__(self):
        super().__init__(URLParameters(
            base_url="https://www.brookings.edu/research-commentary/",
            search_params={"qry": "china"},
        ))


class AEIURLBuilder(BaseURLBuilder):
    """美國企業研究所的URL構建器"""

    def __init__(self):
        super().__init__(URLParameters(
            base_url="https://www.aei.org/search-results/",
            search_params={"wpsolr_q": "china"},
            type_param_key="wpsolr_fq[0]",
            type_param_format="type:{type}",
            page_param_key="wpsolr_page",
            page_param_format="{page}"
        ))


class RANDURLBuilder(BaseURLBuilder):
    """RAND智庫的URL構建器"""

    def __init__(self):
        def calculate_start(page: int) -> str:
            try:
                return str((int(page) - 1) * 48)
            except (TypeError, ValueError):
                return "0"

        super().__init__(URLParameters(
            base_url="https://www.rand.org/search.html",
            search_params={
                "q": "china",
                # "content_type_s": "Report",
                "sortby": "date_dt",
                "rows": "48"
            },
            type_param_key="content_type_s",
            type_param_format="{type}",
            page_param_key="start",
            page_param_format=calculate_start
        ))


class HeritageURLBuilder(BaseURLBuilder):
    """美國傳統基金會的URL構建器"""

    def __init__(self):
        super().__init__(URLParameters(
            base_url="https://www.heritage.org/china",
            filter_params={
                "taxonomy_term_tid": "132",
            },
            type_param_key="f[0]",
            type_param_format="content_type:{type}",
            page_param_key="page",
            page_param_format="{page}",
            show_first_page_param=True
        ))


class AmericanProgressURLBuilder(BaseURLBuilder):
    """美國進步中心的URL構建器"""

    def __init__(self):
        super().__init__(URLParameters(
            base_url="https://www.americanprogress.org/",
            search_params={"s": "China"}
        ))
