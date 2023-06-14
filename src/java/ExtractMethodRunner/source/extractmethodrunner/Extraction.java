/*
 * Copyright (c) 2002 - 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package extractmethodrunner;

import org.eclipse.ltk.core.refactoring.Change;

public interface Extraction extends Comparable<Extraction> {

	int start();
	
	int end();
	
	Change change();
	
	default boolean overlaps(Extraction e) {
		return !(end() < e.start() || start() > e.end());
	}

	@Override
	default int compareTo(Extraction o) {
		return start() != o.start()? o.start() - start(): end() - o.end();
	}
}
