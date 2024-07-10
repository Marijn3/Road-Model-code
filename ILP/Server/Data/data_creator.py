import json

data_file="data_a16_a58.json"

data = {
    "RSU_A16_R_65_5": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_R_66_2": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_65_5,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_65_5,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_6,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": "[RSU_A16_R_66_6,4]",
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_65_5,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_R_66_6": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_8,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
            "4": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_66_8,4]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": "[RSU_A16_R_66_2,3]",
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_R_66_8": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_67_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_67_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_67_4g,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_6,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
            "4": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_67_4g,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_6,4]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_R_67_6": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_68_5,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_R_68_5,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_66_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_R_68_5": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_67_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_67_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },

    "RSU_A16_L_65_5": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_L_66_2": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_65_5,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_65_5,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_65_5,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_66_8,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_L_66_8": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_66_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_67_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_66_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_67_8,2]",
                    "Secondary": None,
                    "Taper": "[RSU_A58_R_62_7r,1]",
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_66_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_62_7r,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_L_67_8": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_66_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_68_5,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_66_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_68_5,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A16_L_68_5": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_67_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_67_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A16_L_67_9f,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },

    "RSU_A58_R_62_1": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_7,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_7r,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_7r,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_8,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_R_61_8": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_1,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_1,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_62_1,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_61_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_R_61_2": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_61_8,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_60_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": 20
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_61_8,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_60_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": 0,
                    "Right": None
                },
                "Carriageway": "2",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_61_8,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": "[RSU_A58_R_60_6,2]",
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "2",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "2",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_R_60_6": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_61_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_60_1,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_61_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": "[RSU_A58_R_61_2,3]",
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_R_60_1,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_R_60_1": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_60_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_R_60_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },

    "RSU_A58_L_62_7": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_61_9,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_67_4g,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_61_9,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_R_67_4g,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_L_61_9": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_61_2,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_62_7,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_61_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_62_7,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_61_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A16_L_67_9f,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_L_61_2": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": "[RSU_A58_L_60_6,1]",
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_61_9,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_60_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_61_9,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "3": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_60_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_61_9,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_L_60_6": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_60_1,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_61_2,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": "[RSU_A58_L_61_2,1]",
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": "[RSU_A58_L_60_1,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_61_2,3]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },
    "RSU_A58_L_60_1": {
        "MSI": {
            "1": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_60_6,1]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
            "2": {
                "Downstream": {
                    "Primary": None,
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "Upstream": {
                    "Primary": "[RSU_A58_L_60_6,2]",
                    "Secondary": None,
                    "Taper": None,
                    "Broadening": None,
                    "Narrowing": None,
                },
                "State": None,
                "TrafficStream": "1",
                "TrafficStream_Influence": {
                    "Left": None,
                    "Right": None
                },
                "Carriageway": "1",
            },
        },
        "Continue-V": False,
        "Continue-X": False,
        "Stat-V": 100,
        "Dyn-V": None,
    },

    "RSU_A16_R_67_4g": {
            "MSI": {
                "1": {
                    "Downstream": {
                        "Primary": "[RSU_A58_L_62_7,1]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A16_R_66_8,3]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
                "2": {
                    "Downstream": {
                        "Primary": "[RSU_A58_L_62_7,2]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A16_R_66_8,4]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
            },
            "Continue-V": False,
            "Continue-X": False,
            "Stat-V": 100,
            "Dyn-V": None,
        },
    "RSU_A58_R_62_7r": {
            "MSI": {
                "1": {
                    "Downstream": {
                        "Primary": None,
                        "Secondary": None,
                        "Taper": "[RSU_A16_L_66_8,2]",
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A58_R_62_1,2]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
                "2": {
                    "Downstream": {
                        "Primary": "[RSU_A16_L_66_8,3]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A58_R_62_1,3]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
            },
            "Continue-V": False,
            "Continue-X": False,
            "Stat-V": 100,
            "Dyn-V": None,
        },
    "RSU_A58_R_62_7": {
            "MSI": {
                "1": {
                    "Downstream": {
                        "Primary": None,
                        "Secondary": "[RSU_A16_R_68_5,2]",
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A58_R_62_1,1]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
            },
            "Continue-V": False,
            "Continue-X": False,
            "Stat-V": 100,
            "Dyn-V": None,
        },
    "RSU_A16_L_67_9f": {
            "MSI": {
                "1": {
                    "Downstream": {
                        "Primary": "[RSU_A58_L_61_9,3]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "Upstream": {
                        "Primary": "[RSU_A16_L_68_5,3]",
                        "Secondary": None,
                        "Taper": None,
                        "Broadening": None,
                        "Narrowing": None,
                    },
                    "State": None,
                    "TrafficStream": "1",
                    "TrafficStream_Influence": {
                        "Left": None,
                        "Right": None
                    },
                    "Carriageway": "1",
                },
            },
            "Continue-V": False,
            "Continue-X": False,
            "Stat-V": 100,
            "Dyn-V": None,
        },
        
}


with open(data_file, "w") as outfile:
    json.dump(data, outfile)
