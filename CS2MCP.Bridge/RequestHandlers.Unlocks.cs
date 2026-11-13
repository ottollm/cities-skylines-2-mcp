using System;
using System.Collections.Generic;
using Game.Prefabs;
using Unity.Collections;
using Unity.Entities;

namespace CS2MCP
{
    /// <summary>
    /// Why is a prefab locked? Lists each unlock requirement of prefabs whose name contains ?name=,
    /// with the requirement's own lock state and what it asks for (built objects, population,
    /// zone squares, dev-tree node...). Read-only.
    /// </summary>
    public sealed partial class RequestHandlers
    {
        private object DescribeRequirement(PrefabSystem prefabSystem, Entity req)
        {
            var d = new Dictionary<string, object>
            {
                ["name"] = PrefabName(prefabSystem, req),
                ["met"] = !IsLocked(req),
            };
            if (EntityManager.HasComponent<UnlockRequirementData>(req))
            {
                d["progress"] = EntityManager.GetComponentData<UnlockRequirementData>(req).m_Progress;
            }
            if (EntityManager.HasComponent<StrictObjectBuiltRequirementData>(req))
            {
                StrictObjectBuiltRequirementData s = EntityManager.GetComponentData<StrictObjectBuiltRequirementData>(req);
                d["kind"] = "build this exact prefab";
                d["prefab"] = PrefabName(prefabSystem, s.m_Requirement);
                d["minimumCount"] = s.m_MinimumCount;
            }
            if (EntityManager.HasComponent<ObjectBuiltRequirementData>(req))
            {
                d["kind"] = "build objects";
                d["minimumCount"] = EntityManager.GetComponentData<ObjectBuiltRequirementData>(req).m_MinimumCount;
            }
            if (EntityManager.HasComponent<CitizenRequirementData>(req))
            {
                CitizenRequirementData c = EntityManager.GetComponentData<CitizenRequirementData>(req);
                d["kind"] = "population";
                d["minimumPopulation"] = c.m_MinimumPopulation;
                d["minimumHappiness"] = c.m_MinimumHappiness;
            }
            if (EntityManager.HasComponent<ZoneBuiltRequirementData>(req))
            {
                ZoneBuiltRequirementData z = EntityManager.GetComponentData<ZoneBuiltRequirementData>(req);
                d["kind"] = "zone built";
                d["zone"] = PrefabName(prefabSystem, z.m_RequiredZone);
                d["minimumSquares"] = z.m_MinimumSquares;
                d["minimumCount"] = z.m_MinimumCount;
                d["minimumLevel"] = z.m_MinimumLevel;
            }
            if (EntityManager.HasComponent<DevTreeNodeData>(req))
            {
                d["kind"] = "development tree node";
                d["cost"] = EntityManager.GetComponentData<DevTreeNodeData>(req).m_Cost;
            }
            if (EntityManager.HasComponent<TransportRequirementData>(req))
            {
                TransportRequirementData t = EntityManager.GetComponentData<TransportRequirementData>(req);
                d["kind"] = "transport usage";
                d["building"] = PrefabName(prefabSystem, t.m_BuildingPrefab);
                d["minimumPassengers"] = t.m_MinimumTransportedPassenger;
            }
            if (EntityManager.HasBuffer<UnlockRequirement>(req))
            {
                DynamicBuffer<UnlockRequirement> sub = EntityManager.GetBuffer<UnlockRequirement>(req, isReadOnly: true);
                var names = new List<string>();
                for (int i = 0; i < sub.Length && i < 8; i++)
                {
                    names.Add(PrefabName(prefabSystem, sub[i].m_Prefab) + (IsLocked(sub[i].m_Prefab) ? " (locked)" : " (met)"));
                }
                d["needs"] = names;
            }
            return d;
        }

        private BridgeResponse GetUnlockRequirements(BridgeRequest request)
        {
            request.Query.TryGetValue("name", out string q);
            q = q ?? "";
            int limit = 15;
            if (request.Query.TryGetValue("limit", out string ls) && int.TryParse(ls, out int li))
            {
                limit = Math.Max(1, Math.Min(5000, li));
            }
            bool lockedOnly = !(request.TryGetBool("all", out bool a) && a);
            PrefabSystem prefabSystem = World.GetOrCreateSystemManaged<PrefabSystem>();
            var items = new List<object>();
            using (EntityQuery query = EntityManager.CreateEntityQuery(ComponentType.ReadOnly<PrefabData>(), ComponentType.ReadOnly<UnlockRequirement>()))
            using (NativeArray<Entity> ents = query.ToEntityArray(Allocator.Temp))
            {
                foreach (Entity e in ents)
                {
                    string name = PrefabName(prefabSystem, e);
                    if (name == null || (q.Length > 0 && name.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0))
                    {
                        continue;
                    }
                    bool locked = IsLocked(e);
                    if (lockedOnly && !locked)
                    {
                        continue;
                    }
                    DynamicBuffer<UnlockRequirement> reqs = EntityManager.GetBuffer<UnlockRequirement>(e, isReadOnly: true);
                    var list = new List<object>();
                    for (int i = 0; i < reqs.Length; i++)
                    {
                        if (reqs[i].m_Prefab == e)
                        {
                            continue;
                        }
                        var r = (Dictionary<string, object>)DescribeRequirement(prefabSystem, reqs[i].m_Prefab);
                        r["flags"] = reqs[i].m_Flags.ToString();
                        list.Add(r);
                    }
                    items.Add(new { name, locked, requirements = list });
                    if (items.Count >= limit)
                    {
                        break;
                    }
                }
            }
            return BridgeResponse.Json(new
            {
                note = "locked prefabs matching ?name= and what each still needs (&all=true includes unlocked ones)",
                stalenessWarning = LockStalenessWarning,
                items,
            });
        }
    }
}
