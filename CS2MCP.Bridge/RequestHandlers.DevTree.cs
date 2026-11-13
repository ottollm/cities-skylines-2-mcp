using System;
using System.Collections.Generic;
using Game.City;
using Game.Prefabs;
using Unity.Collections;
using Unity.Entities;

namespace CS2MCP
{
    /// <summary>
    /// Development tree (Progression panel): list nodes with cost, requirements and what each
    /// unlocks, and purchase a node with development points through DevTreeSystem.Purchase -
    /// the same call the game's DevTreeUISystem makes when the player clicks "Unlock".
    /// </summary>
    public sealed partial class RequestHandlers
    {
        private int GetDevTreePoints()
        {
            using (EntityQuery q = EntityManager.CreateEntityQuery(ComponentType.ReadOnly<DevTreePoints>()))
            using (NativeArray<Entity> e = q.ToEntityArray(Allocator.Temp))
            {
                return e.Length > 0 ? EntityManager.GetComponentData<DevTreePoints>(e[0]).m_Points : 0;
            }
        }

        /// <summary>Prefab entity -> names of locked-or-not prefabs that list it as an unlock requirement.</summary>
        private Dictionary<Entity, List<string>> UnlockedBy(PrefabSystem prefabSystem)
        {
            var map = new Dictionary<Entity, List<string>>();
            using (EntityQuery q = EntityManager.CreateEntityQuery(ComponentType.ReadOnly<UnlockRequirement>(), ComponentType.ReadOnly<PrefabData>()))
            using (NativeArray<Entity> ents = q.ToEntityArray(Allocator.Temp))
            {
                foreach (Entity e in ents)
                {
                    DynamicBuffer<UnlockRequirement> reqs = EntityManager.GetBuffer<UnlockRequirement>(e, isReadOnly: true);
                    string name = null;
                    for (int i = 0; i < reqs.Length; i++)
                    {
                        if (reqs[i].m_Prefab == e || !EntityManager.HasComponent<DevTreeNodeData>(reqs[i].m_Prefab))
                        {
                            continue;
                        }
                        if (name == null)
                        {
                            PrefabBase p = prefabSystem.GetPrefab<PrefabBase>(e);
                            name = p != null ? p.name : e.ToString();
                        }
                        if (!map.TryGetValue(reqs[i].m_Prefab, out List<string> list))
                        {
                            map[reqs[i].m_Prefab] = list = new List<string>();
                        }
                        list.Add(name);
                    }
                }
            }
            return map;
        }

        private string PrefabName(PrefabSystem prefabSystem, Entity e)
        {
            if (e == Entity.Null)
            {
                return null;
            }
            PrefabBase p = prefabSystem.GetPrefab<PrefabBase>(e);
            return p != null ? p.name : e.ToString();
        }

        private BridgeResponse GetDevTree(BridgeRequest request)
        {
            if (!TryGetCity(out _, out BridgeResponse error))
            {
                return error;
            }
            request.Query.TryGetValue("service", out string serviceFilter);
            bool all = request.TryGetBool("all", out bool a) && a;

            PrefabSystem prefabSystem = World.GetOrCreateSystemManaged<PrefabSystem>();
            Dictionary<Entity, List<string>> unlocks = UnlockedBy(prefabSystem);
            int points = GetDevTreePoints();
            var nodes = new List<object>();
            using (EntityQuery q = EntityManager.CreateEntityQuery(ComponentType.ReadOnly<DevTreeNodeData>(), ComponentType.ReadOnly<PrefabData>()))
            using (NativeArray<Entity> ents = q.ToEntityArray(Allocator.Temp))
            {
                foreach (Entity e in ents)
                {
                    DevTreeNodeData data = EntityManager.GetComponentData<DevTreeNodeData>(e);
                    string service = PrefabName(prefabSystem, data.m_Service);
                    if (!string.IsNullOrEmpty(serviceFilter) && (service == null || service.IndexOf(serviceFilter, StringComparison.OrdinalIgnoreCase) < 0))
                    {
                        continue;
                    }
                    bool purchased = !IsLocked(e);
                    if (purchased && !all)
                    {
                        continue;
                    }
                    var requires = new List<string>();
                    bool reqMet = true;
                    if (EntityManager.HasBuffer<DevTreeNodeRequirement>(e))
                    {
                        DynamicBuffer<DevTreeNodeRequirement> r = EntityManager.GetBuffer<DevTreeNodeRequirement>(e, isReadOnly: true);
                        for (int i = 0; i < r.Length; i++)
                        {
                            if (r[i].m_Node == Entity.Null)
                            {
                                continue;
                            }
                            requires.Add(PrefabName(prefabSystem, r[i].m_Node));
                            reqMet &= !IsLocked(r[i].m_Node);
                        }
                    }
                    bool serviceUnlocked = data.m_Service == Entity.Null || !IsLocked(data.m_Service);
                    unlocks.TryGetValue(e, out List<string> u);
                    nodes.Add(new
                    {
                        name = PrefabName(prefabSystem, e),
                        service,
                        cost = data.m_Cost,
                        purchased,
                        canBuyNow = !purchased && reqMet && serviceUnlocked && data.m_Cost <= points,
                        serviceUnlocked,
                        requires,
                        unlocks = u ?? new List<string>(),
                    });
                }
            }

            return BridgeResponse.Json(new
            {
                points,
                note = "buy with POST /city/devtree/buy?node=<name>. Lists unpurchased nodes; &all=true includes purchased, &service=<text> filters. " +
                       "A node needs its service unlocked (milestones), its 'requires' nodes purchased and cost <= points.",
                stalenessWarning = LockStalenessWarning,
                nodes,
            });
        }

        private BridgeResponse BuyDevTreeNode(BridgeRequest request)
        {
            if (!TryGetCity(out _, out BridgeResponse error))
            {
                return error;
            }
            if (!request.Query.TryGetValue("node", out string nodeName) || string.IsNullOrEmpty(nodeName))
            {
                return BridgeResponse.Error(400, "provide ?node=<name from /city/devtree>");
            }

            PrefabSystem prefabSystem = World.GetOrCreateSystemManaged<PrefabSystem>();
            using (EntityQuery q = EntityManager.CreateEntityQuery(ComponentType.ReadOnly<DevTreeNodeData>(), ComponentType.ReadOnly<PrefabData>()))
            using (NativeArray<Entity> ents = q.ToEntityArray(Allocator.Temp))
            {
                foreach (Entity e in ents)
                {
                    if (!string.Equals(PrefabName(prefabSystem, e), nodeName, StringComparison.OrdinalIgnoreCase))
                    {
                        continue;
                    }
                    DevTreeNodeData data = EntityManager.GetComponentData<DevTreeNodeData>(e);
                    int points = GetDevTreePoints();
                    if (!IsLocked(e))
                    {
                        return BridgeResponse.Error(409, $"'{nodeName}' is already purchased");
                    }
                    if (data.m_Service != Entity.Null && IsLocked(data.m_Service))
                    {
                        return BridgeResponse.Error(409, $"service '{PrefabName(prefabSystem, data.m_Service)}' is not unlocked yet (needs a milestone)");
                    }
                    if (EntityManager.HasBuffer<DevTreeNodeRequirement>(e))
                    {
                        DynamicBuffer<DevTreeNodeRequirement> r = EntityManager.GetBuffer<DevTreeNodeRequirement>(e, isReadOnly: true);
                        for (int i = 0; i < r.Length; i++)
                        {
                            if (r[i].m_Node != Entity.Null && IsLocked(r[i].m_Node))
                            {
                                return BridgeResponse.Error(409, $"buy '{PrefabName(prefabSystem, r[i].m_Node)}' first");
                            }
                        }
                    }
                    if (data.m_Cost > points)
                    {
                        return BridgeResponse.Error(409, $"costs {data.m_Cost} points, you have {points}");
                    }

                    World.GetOrCreateSystemManaged<DevTreeSystem>().Purchase(e);
                    return BridgeResponse.Json(new
                    {
                        node = PrefabName(prefabSystem, e),
                        cost = data.m_Cost,
                        pointsBefore = points,
                        note = "unlock is applied at end of frame; unpause briefly before relying on 'locked' flags",
                    });
                }
            }
            return BridgeResponse.Error(404, $"unknown node '{nodeName}'; list names via /city/devtree");
        }
    }
}
