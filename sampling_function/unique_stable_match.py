def gale_shapley(prefs):
    # Workers are proposing

    # Generating list of worker/firm labels, e.g. W1, F3
    workers = [k for k in prefs["workers"].keys()]
    firms = [k for k in prefs["firms"].keys()]

    # Initializing rejection sets for each worker
    # Elements of set will be Firm labels, e.g. F1, F3
    rejections = { worker: set() for worker in workers}

    # Array of available suitors, initially all workers are available suitors
    available_suitors = [worker for worker in workers]

    # Generating object that contains matches, for each match, a pair of items will be in this
    # (W1, F1) yields two items: "W1": "F1" and "F1: W1"
    # Items in Python objects are always in the form, key: value
    matches = {agent: None for agent in workers + firms}

    # Keep running algorithm until there are no available suitors
    while len(available_suitors) > 0:

        # Initializing proposal array for each firm, firms are receiving proposals
        proposals = { firm: [] for firm in firms}

        # Only available suitors can make proposals
        for worker in available_suitors:

            # potential_match is best firm that a given worker has not been rejected by
            potential_match = [firm for firm in prefs["workers"][worker] if firm not in rejections[worker]][0]
            # Including proposal from a given worker to potential_match's proposals
            proposals[potential_match].append(worker)
        
        # After workers make proposals, all firms accept their best proposals
        for firm in firms:

            # proposals[firm] is an array of proposals and returns true if it is not empty
            # So if a given firm has any proposals...continue
            if proposals[firm]:
                
                # If I am currently matched, add my match to my list of proposals
                # My match has to always compete against my proposals
                if matches[firm]:
                    proposals[firm].append(matches[firm])
                    available_suitors.append(matches[firm])
                
                # Getting preference ranks from all of my proposals
                proposal_ranks = [prefs["firms"][firm].index(worker) for worker in proposals[firm]]
                
                # Choosing the best ranked worker
                best_proposal = prefs["firms"][firm][min(proposal_ranks)]
                
                matches[firm] = best_proposal
                matches[best_proposal] = firm

                available_suitors.remove(best_proposal)

                # Any worker that wasn't chosen was rejected so this firm is added to the set of rejections
                for worker in proposals[firm]:
                    if worker != matches[firm]:
                        rejections[worker].add(firm)

    return matches


def has_unique_stable_match(prefs):
    worker_optimal_match = gale_shapley(prefs)

    switched_prefs = {
        "workers": prefs["firms"],
        "firms": prefs["workers"]
    }

    firm_optimal_match = gale_shapley(switched_prefs)

    return worker_optimal_match == firm_optimal_match