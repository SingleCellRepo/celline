from celline.functions._base import CellineFunction
from celline.plugins.collections.generic import DictionaryC, ListC
from typing import Optional, List, Dict
from celline.database import NCBI


class Add(CellineFunction):
    def register(self) -> str:
        return "add"

    def on_call(self, args: Dict[str, DictionaryC[str, Optional[str]]]):
        options = args["options"]
        id = options["req_1"]
        if id is not None:
            NCBI.add(id)
        return


# import inquirer
# import inquirer.themes as themes
# from tqdm import tqdm
# from celline.functions._base import CellineFunction
# from celline.plugins.collections.generic import DictionaryC, ListC
# from typing import Optional, List, Dict
# from celline.data.manager import DataManager
# from celline.data.SRAData import SRAData
# from celline.ncbi.SRAID import SRAID
# from celline.GEO.GSE import GSE
# from celline.GEO.GSM import GSM

# import asyncio


# class Add(CellineFunction):
#     """
#     Add SRR run
#     """

#     def register(self) -> str:
#         return "add"

#     def get_runID(self, options: DictionaryC[str, Optional[str]]):
#         if not options.ContainsKey("req_1"):
#             print("[ERROR] Please specify Run ID.")
#             quit()
#         run_id = options["req_1"]
#         if run_id is None:
#             print("[ERROR] Run ID is invalid.")
#             quit()
#         # if (not run_id.startswith("SRR")) and (not run_id.startswith("GSM")):
#         #     print("[ERROR] Please specify SRR or GSM ID.")
#         #     quit()
#         return run_id

#     def on_call(self, args: Dict[str, DictionaryC[str, Optional[str]]]):
#         options = args["options"]
#         run_id = self.get_runID(options)
#         __sample_name = options["name"]
#         if __sample_name is not None:
#             sample_name: str = __sample_name
#         else:
#             sample_name = input("Sample name?: ")

#         def add_fromsrr_internal(_srr_id: str):
#             asyncio.get_event_loop().run_until_complete(
#                 DataManager.add_fromSRRID(
#                     sample_name,
#                     _srr_id,
#                     force_update=options.ContainsKey("update"),
#                     quiet=options.ContainsKey("quiet"),
#                 )
#             )
#         if run_id.startswith("SRR"):
#             if not DataManager.contains_run_id(run_id) or options.ContainsKey("update"):
#                 add_fromsrr_internal(run_id)
#             else:
#                 print(
#                     f"[Info] Skipped addition of {run_id} (If you wish to update info, please specify --update)"
#                 )
#         elif run_id.startswith("GSM"):
#             target_srrs = GSM(gsm_id=run_id).get_sra_runid()
#             for i in tqdm(range(len(target_srrs)), desc="Fetching SRR"):
#                 if not DataManager.contains_run_id(target_srrs[i]) or options.ContainsKey("update"):
#                     add_fromsrr_internal(target_srrs[i])
#                 else:
#                     print(
#                         f"[Info] Skipped addition of {run_id} (If you wish to update info, please specify --update)"
#                     )
#         elif run_id.startswith("GSE"):
#             gse = GSE(run_id)
#             questions = [inquirer.Checkbox(
#                 "target_gsms",
#                 message="Choose dump target GSM IDs",
#                 choices=gse.child_gsms_id,
#                 carousel=True,
#                 default=gse.child_gsms_id
#             )]
#             answers = inquirer.prompt(
#                 questions,
#                 theme=themes.GreenPassion(),
#                 raise_keyboard_interrupt=True
#             )
#             if answers is not None:
#                 fetched: List[GSM] = []
#                 target_gsms = answers['target_gsms']
#                 for i in tqdm(range(len(target_gsms)), desc="Fetching GSM"):
#                     fetched.append(GSM(target_gsms[i]))
#                 print("Fetching GSM: complete.")
#                 for i in tqdm(range(len(fetched)), desc="Fetching SRA"):
#                     targetd = fetched[i]
#                     for fetchedrunid in targetd.get_sra_runid():
#                         if not DataManager.contains_run_id(fetchedrunid) or options.ContainsKey("update"):
#                             add_fromsrr_internal(fetchedrunid)
#                         else:
#                             print(
#                                 f"[Info] Skipped addition of {run_id} (If you wish to update info, please specify --update)"
#                             )

#         else:
#             print(f"[ERROR] Unknown identifier: {run_id}")
#             # questions = [inquirer.Checkbox(
#             #     'interests',
#             #     message="What are you interested in?",
#             #     choices=['Computers', 'Books', 'Science',
#             #              'Nature', 'Fantasy', 'History'],
#             # )]
#             # answers = inquirer.prompt(questions)  # returns a dict
#             # print(answers['interests'])
#             quit()
#         return
