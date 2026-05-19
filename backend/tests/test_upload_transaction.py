import src.uploadTransaction as uploadTransaction

def test_run(seeded_db):
    pass


def test_valid_user(seeded_db):
    assert uploadTransaction.validUser(1) == True
    assert uploadTransaction.validUser(2) == False

def test_run_json(seeded_db):
    pass


def test_get_arrays_by_dict(seeded_db):
    pass


# dictData = {
#         1: {
#             'value': 27.15,
#             'date': '2026-05-19',
#             'info': "test information",
#             'group': 'purchase',
#             'category': 'misc'
#         },

#         2: {
#             'value': 27.15,
#             'date': '2026-05-19',
#             'info': "test information",
#             'group': 'purchase',
#             'category': 'misc'
#         },

#         3: {
#             'value': 27.15,
#             'date': '2026-05-19',
#             'info': "test information",
#             'group': 'transfer',
#             'category': 'misc'
#         }
#     }